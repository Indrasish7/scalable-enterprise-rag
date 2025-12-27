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


# -------------------------------------------------
# Helper: Stable document ID
# -------------------------------------------------
def generate_stable_doc_id(filename: str, text: str) -> str:
    """
    Generate a deterministic document ID based on filename + content.
    Same file -> same ID, modified file -> new ID.
    """
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{filename}:{content_hash}"


# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Scalable Enterprise RAG",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Scalable Enterprise RAG System")
st.caption("Production-grade Retrieval-Augmented Generation with FAISS + Gemini")


# -------------------------------------------------
# Session state (persistent objects)
# -------------------------------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "vector_store_ready" not in st.session_state:
    st.session_state.vector_store_ready = False

if "kb_manager" not in st.session_state:
    st.session_state.kb_manager = KnowledgeBaseManager()


# -------------------------------------------------
# Incremental pipeline builder (NO caching)
# -------------------------------------------------
def build_pipeline_incremental(
    raw_docs: List[dict],
    vector_store: FaissVectorStore | None,
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

        # Clean
        cleaned_docs = cleaner.clean_documents([doc])
        if not cleaned_docs:
            continue

        # Chunk
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

        # Batch embedding
        if texts_to_embed:
            vectors = embedder.embed(texts_to_embed)
            for chunk, vector in zip(chunk_refs, vectors):
                cache.set(chunk["text"], vector)
                all_embeddings.append(vector)
                all_metadatas.append({
                    **chunk["metadata"],
                    "text": chunk["text"]
                })

        # ✅ Update KB state only after successful ingestion
        kb_manager.update_doc(doc_id, text)

    if not all_embeddings:
        raise ValueError("No new or updated documents to ingest.")

    # 🔒 Persistent FAISS index
    if vector_store is None:
        vector_store = FaissVectorStore(vector_dim=len(all_embeddings[0]))

    vector_store.add(all_embeddings, all_metadatas)

    retriever = Retriever(embedder, vector_store)
    llm = GeminiLLM()

    return RAGPipeline(retriever, llm), vector_store


# -------------------------------------------------
# Sidebar: Knowledge Base Management
# -------------------------------------------------
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

                    ext = uploaded_file.name.split(".")[-1]
                    loader = get_loader(ext)

                    docs = loader.load(file_path)

                    # ✅ Assign stable document IDs here
                    for doc in docs:
                        doc["id"] = generate_stable_doc_id(
                            uploaded_file.name,
                            doc["text"]
                        )

                    raw_docs.extend(docs)

            try:
                pipeline, st.session_state.vector_store = build_pipeline_incremental(
                    raw_docs,
                    st.session_state.vector_store,
                    st.session_state.kb_manager
                )

                st.session_state.pipeline = pipeline
                st.session_state.vector_store_ready = True
                st.sidebar.success("Knowledge base updated successfully!")

            except Exception as e:
                st.sidebar.warning(str(e))


# -------------------------------------------------
# Main: Question Answering
# -------------------------------------------------
st.header("💬 Ask a Question")

query = st.text_input(
    "Enter your question",
    placeholder="What did Apple announce?"
)

if st.button("Get Answer"):
    if not st.session_state.vector_store_ready:
        st.error("Please build the knowledge base first.")
    elif not query.strip():
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Generating answer with observability..."):
            result = st.session_state.pipeline.answer_with_observability(query)

        # Answer
        st.subheader("✅ Answer")
        st.write(result["answer"])

        # Metrics
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

        # Context transparency
        with st.expander("📚 Retrieved Contexts"):
            for i, chunk in enumerate(result["retrieved_chunks"], 1):
                st.markdown(f"**Context {i}**")
                st.write(chunk["metadata"]["text"][:600])
