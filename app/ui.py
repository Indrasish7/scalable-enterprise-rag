import streamlit as st
from typing import List
import tempfile
import os
import hashlib

from ingestion.loaders import get_loader
from ingestion.cleaner import TextCleaner
from chunking.strategies import FixedSizeChunker
from embeddings.embedder import GeminiEmbedder
from embeddings.cache import EmbeddingCache
from vectorstore.faiss_store import FaissVectorStore
from vectorstore.kb_manager import KnowledgeBaseManager
from retrieval.retriever import Retriever
from llm.gemini_llm import GeminiLLM
from rag.pipeline import RAGPipeline


# =================================================
# Constants
# =================================================
EMBEDDING_DIM = 768  # Gemini embedding dimension


# =================================================
# Helper: Stable document ID
# =================================================
def generate_stable_doc_id(filename: str, text: str) -> str:
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{filename}:{content_hash}"


# =================================================
# Page configuration
# =================================================
st.set_page_config(
    page_title="Scalable Enterprise RAG",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Scalable Enterprise RAG System")
st.caption("Production-grade Retrieval-Augmented Generation with FAISS + Gemini")


# =================================================
# Session state initialization
# =================================================
if "vector_store" not in st.session_state:
    st.session_state.vector_store = FaissVectorStore(
        vector_dim=EMBEDDING_DIM
    )

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "vector_store_ready" not in st.session_state:
    st.session_state.vector_store_ready = False

if "kb_manager" not in st.session_state:
    st.session_state.kb_manager = KnowledgeBaseManager()


# =================================================
# AUTO-ENABLE PIPELINE IF KB EXISTS (CRITICAL FIX)
# =================================================
if (
    st.session_state.vector_store is not None
    and st.session_state.vector_store.index.ntotal > 0
    and st.session_state.pipeline is None
):
    retriever = Retriever(GeminiEmbedder(), st.session_state.vector_store)
    llm = GeminiLLM()
    st.session_state.pipeline = RAGPipeline(retriever, llm)
    st.session_state.vector_store_ready = True


# =================================================
# Incremental ingestion + pipeline builder
# =================================================
def build_pipeline_incremental(
    raw_docs: List[dict],
    vector_store: FaissVectorStore,
    kb_manager: KnowledgeBaseManager
):
    cleaner = TextCleaner()
    chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    embedder = GeminiEmbedder()
    cache = EmbeddingCache()

    all_embeddings = []
    all_metadatas = []

    for doc in raw_docs:
        doc_id = doc["id"]
        text = doc["text"]

        # 🔁 Incremental change detection
        if not kb_manager.is_new_or_updated(doc_id, text):
            continue

        cleaned_docs = cleaner.clean_documents([doc])
        if not cleaned_docs:
            continue

        chunks = chunker.chunk(cleaned_docs)
        if not chunks:
            continue

        texts_to_embed = []
        chunk_refs = []

        for chunk in chunks:
            cached = cache.get(chunk["text"])
            if cached:
                all_embeddings.append(cached)
                all_metadatas.append({**chunk["metadata"], "text": chunk["text"]})
            else:
                texts_to_embed.append(chunk["text"])
                chunk_refs.append(chunk)

        if texts_to_embed:
            vectors = embedder.embed(texts_to_embed)
            for chunk, vector in zip(chunk_refs, vectors):
                cache.set(chunk["text"], vector)
                all_embeddings.append(vector)
                all_metadatas.append({
                    **chunk["metadata"],
                    "text": chunk["text"]
                })

        # ✅ Persist KB state only after successful ingestion
        kb_manager.update_doc(doc_id, text)

    # =================================================
    # 🔑 UX FIX: No new docs, but KB already exists
    # =================================================
    if not all_embeddings:
        st.sidebar.info(
            "ℹ️ No new documents detected. Using existing knowledge base."
        )
        retriever = Retriever(embedder, vector_store)
        llm = GeminiLLM()
        return RAGPipeline(retriever, llm), vector_store

    # =================================================
    # Add new vectors to FAISS
    # =================================================
    vector_store.add(all_embeddings, all_metadatas)

    retriever = Retriever(embedder, vector_store)
    llm = GeminiLLM()

    return RAGPipeline(retriever, llm), vector_store


# =================================================
# Sidebar: Knowledge Base Management
# =================================================
st.sidebar.header("📄 Knowledge Base")

uploaded_files = st.sidebar.file_uploader(
    "Upload documents (TXT, PDF, DOCX)",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

if st.sidebar.button("Build / Update Knowledge Base"):
    if not uploaded_files:
        st.sidebar.error("Please upload at least one document.")
    else:
        with st.spinner("Updating knowledge base..."):
            raw_docs = []

            with tempfile.TemporaryDirectory() as tmpdir:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(tmpdir, uploaded_file.name)

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.read())

                    loader = get_loader(uploaded_file.name.split(".")[-1])
                    docs = loader.load(file_path)

                    for doc in docs:
                        doc["id"] = generate_stable_doc_id(
                            uploaded_file.name,
                            doc["text"]
                        )

                    raw_docs.extend(docs)

            pipeline, st.session_state.vector_store = build_pipeline_incremental(
                raw_docs,
                st.session_state.vector_store,
                st.session_state.kb_manager
            )

            st.session_state.pipeline = pipeline
            st.session_state.vector_store_ready = True
            st.sidebar.success("Knowledge base ready!")


# =================================================
# Main: Question Answering
# =================================================
st.header("💬 Ask a Question")

query = st.text_input(
    "Enter your question",
    placeholder="What did Apple announce?"
)

if st.button("Get Answer"):
    if st.session_state.pipeline is None:
        st.error("Knowledge base not ready yet.")
    elif not query.strip():
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Generating answer..."):
            result = st.session_state.pipeline.answer_with_observability(query)

        st.subheader("✅ Answer")
        st.write(result["answer"])

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "⏱ Retrieval Latency (ms)",
            f"{result['retrieval_latency_ms']:.2f}"
        )
        col2.metric(
            "📦 Retrieved Chunks",
            result["num_retrieved_chunks"]
        )

        confidence = (
            "🔴 Low" if result["num_retrieved_chunks"] == 0
            else "🟡 Medium" if result["num_retrieved_chunks"] < 3
            else "🟢 High"
        )

        col3.metric("Confidence", confidence)

        with st.expander("📚 Retrieved Contexts"):
            for i, chunk in enumerate(result["retrieved_chunks"], 1):
                st.markdown(f"**Context {i}**")
                st.write(chunk["metadata"]["text"][:600])
