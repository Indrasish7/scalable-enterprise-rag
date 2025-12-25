import streamlit as st
from typing import List

from ingestion.cleaner import TextCleaner
from chunking.strategies import FixedSizeChunker
from embeddings.embedder import DummyEmbedder
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
# Cached pipeline builder (Improvement #1)
# -------------------------------------------------
@st.cache_resource
def build_pipeline(raw_docs: List[dict]) -> RAGPipeline:
    # Clean documents
    cleaner = TextCleaner()
    cleaned_docs = cleaner.clean_documents(raw_docs)

    # Chunk documents
    chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    chunks = chunker.chunk(cleaned_docs)

    # Embed with cache
    embedder = DummyEmbedder()
    cache = EmbeddingCache()

    embeddings = []
    metadatas = []

    for chunk in chunks:
        cached = cache.get(chunk["text"])
        if cached:
            vector = cached
        else:
            vector = embedder.embed([chunk["text"]])[0]
            cache.set(chunk["text"], vector)

        embeddings.append(vector)
        metadatas.append({
            **chunk["metadata"],
            "text": chunk["text"]
        })

    # Build FAISS index
    vector_store = FaissVectorStore(vector_dim=len(embeddings[0]))
    vector_store.add(embeddings, metadatas)

    # Retriever + LLM
    retriever = Retriever(embedder, vector_store)

    try:
        llm = GeminiLLM()
    except Exception as e:
        raise RuntimeError(f"LLM initialization failed: {e}")

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
    "Upload text documents",
    type=["txt"],
    accept_multiple_files=True
)

if st.sidebar.button("Build Knowledge Base"):
    if not uploaded_files:
        st.sidebar.error("Please upload at least one document.")
    else:
        with st.spinner("Processing documents..."):
            raw_docs = []

            for file in uploaded_files:
                content = file.read().decode("utf-8", errors="ignore")
                raw_docs.append({
                    "id": file.name,
                    "text": content,
                    "metadata": {
                        "source": file.name,
                        "type": "txt"
                    }
                })

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
        with st.spinner("Generating answer..."):
            answer = st.session_state.pipeline.answer(query)

        st.subheader("✅ Answer")
        st.write(answer)

        # -------------------------------------------------
        # Retrieved context visibility (Improvement #2)
        # -------------------------------------------------
        with st.expander("📚 Retrieved Contexts"):
            retrieved_chunks = st.session_state.pipeline.retriever.retrieve(query)
            for i, item in enumerate(retrieved_chunks, 1):
                st.markdown(f"**Context {i}**")
                st.write(item["metadata"]["text"][:500])
