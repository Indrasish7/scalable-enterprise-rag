import streamlit as st
from typing import List
import tempfile
import os

from ingestion.loaders import get_loader
from ingestion.cleaner import TextCleaner
from chunking.strategies import FixedSizeChunker
from embeddings.embedder import GeminiEmbedder
from embeddings.cache import EmbeddingCache
from vectorstore.faiss_store import FaissVectorStore
from retrieval.retriever import Retriever
from llm.gemini_llm import GeminiLLM
from rag.pipeline import RAGPipeline


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
# Cached pipeline builder
# (Improvements: batching + safety guard)
# -------------------------------------------------
@st.cache_resource
def build_pipeline(raw_docs: List[dict]) -> RAGPipeline:
    # 1️⃣ Clean documents
    cleaner = TextCleaner()
    cleaned_docs = cleaner.clean_documents(raw_docs)

    if not cleaned_docs:
        raise ValueError("No valid text found after cleaning documents.")

    # 2️⃣ Chunk documents
    chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    chunks = chunker.chunk(cleaned_docs)

    if not chunks:
        raise ValueError("No valid chunks generated from documents.")

    # 3️⃣ Embed with batching + cache
    embedder = GeminiEmbedder()
    cache = EmbeddingCache()

    embeddings = []
    metadatas = []

    texts_to_embed = []
    chunk_indices = []

    for idx, chunk in enumerate(chunks):
        cached_vector = cache.get(chunk["text"])
        if cached_vector:
            embeddings.append(cached_vector)
            metadatas.append({**chunk["metadata"], "text": chunk["text"]})
        else:
            texts_to_embed.append(chunk["text"])
            chunk_indices.append(idx)

    # Batch embedding call (🔥 performance improvement)
    if texts_to_embed:
        new_vectors = embedder.embed(texts_to_embed)

        for idx, vector in zip(chunk_indices, new_vectors):
            cache.set(chunks[idx]["text"], vector)
            embeddings.append(vector)
            metadatas.append({
                **chunks[idx]["metadata"],
                "text": chunks[idx]["text"]
            })

    # 4️⃣ Defensive guard (🔥 correctness improvement)
    if not embeddings:
        raise ValueError("Embedding failed: no vectors generated.")

    # 5️⃣ Build FAISS index
    vector_store = FaissVectorStore(vector_dim=len(embeddings[0]))
    vector_store.add(embeddings, metadatas)

    # 6️⃣ Retriever + LLM + RAG Pipeline
    retriever = Retriever(embedder, vector_store)
    llm = GeminiLLM()

    return RAGPipeline(retriever, llm)


# -------------------------------------------------
# Session state
# -------------------------------------------------
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "vector_store_ready" not in st.session_state:
    st.session_state.vector_store_ready = False


# -------------------------------------------------
# Sidebar: Document ingestion
# -------------------------------------------------
st.sidebar.header("📄 Knowledge Base")

uploaded_files = st.sidebar.file_uploader(
    "Upload documents (TXT, PDF, DOCX)",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

if st.sidebar.button("Build Knowledge Base"):
    if not uploaded_files:
        st.sidebar.error("Please upload at least one document.")
    else:
        with st.spinner("Processing documents..."):
            raw_docs = []

            with tempfile.TemporaryDirectory() as tmpdir:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(tmpdir, uploaded_file.name)

                    # Save uploaded file temporarily
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # Route to correct loader
                    extension = uploaded_file.name.split(".")[-1]
                    loader = get_loader(extension)

                    docs = loader.load(file_path)
                    raw_docs.extend(docs)

            try:
                pipeline = build_pipeline(raw_docs)
                st.session_state.pipeline = pipeline
                st.session_state.vector_store_ready = True
                st.sidebar.success("Knowledge base built successfully!")
            except Exception as e:
                st.sidebar.error(str(e))


# -------------------------------------------------
# Main: Question answering
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

        # -------------------------
        # Answer
        # -------------------------
        st.subheader("✅ Answer")
        st.write(result["answer"])

        # -------------------------
        # Observability Metrics
        # -------------------------
        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="⏱ Retrieval Latency (ms)",
            value=f"{result['retrieval_latency_ms']:.2f}"
        )

        col2.metric(
            label="📦 Retrieved Chunks",
            value=result["num_retrieved_chunks"]
        )

        # Confidence heuristic
        if result["num_retrieved_chunks"] == 0:
            confidence = "Low"
            color = "🔴"
        elif result["num_retrieved_chunks"] < 3:
            confidence = "Medium"
            color = "🟡"
        else:
            confidence = "High"
            color = "🟢"

        col3.metric(
            label="Confidence",
            value=f"{color} {confidence}"
        )

        # -------------------------
        # Retrieved Contexts
        # -------------------------
        with st.expander("📚 Retrieved Contexts"):
            for i, chunk in enumerate(result["retrieved_chunks"], 1):
                st.markdown(f"**Context {i}**")
                st.write(chunk["metadata"]["text"][:600])

