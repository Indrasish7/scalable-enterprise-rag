# 🧠 Scalable Enterprise RAG System

**Production-grade Retrieval-Augmented Generation (RAG) system** designed for enterprise-scale document ingestion, semantic search, and LLM-powered question answering.

This project focuses on **scalability, modularity, system design, and evaluation**, not just demo-level RAG pipelines.

---

## 🚀 Key Features

- Modular **end-to-end RAG architecture**
- **FAISS-based vector search** for high-performance retrieval
- Config-driven pipeline using YAML
- Pluggable chunking strategies
- Embedding caching to reduce recomputation
- Explicit **evaluation layer** (latency & retrieval quality)
- Designed with **enterprise-scale document systems** in mind

---

## 📄 Supported Document Formats

The system supports **multi-format enterprise document ingestion**:

- ✅ **TXT** — Plain text files  
- ✅ **PDF** — Extracted using `pypdf`  
- ✅ **DOCX** — Extracted using `python-docx`

- Multi-format ingestion (TXT, PDF, DOCX) via extensible loader architecture


Documents are automatically routed to the correct loader using a **factory-based ingestion layer**, making it easy to extend support to additional formats such as HTML, Markdown, or PPTX.


---

## 🏗️ System Architecture

```text
┌──────────────┐
│ Raw Documents│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Ingestion     │ ← loaders.py, cleaner.py
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Chunking      │ ← strategies.py
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Embeddings    │ ← embedder.py, cache.py
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Vector Store  │ ← FAISS
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Retrieval     │ ← retriever.py
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LLM Response  │
└──────────────┘
```
---

## 📁 Project Structure
```text

scalable-enterprise-rag/
│
├── app/
│   └── ui.py                 # Streamlit UI for end-to-end RAG interaction
│
├── ingestion/
│   ├── base.py               # BaseLoader abstract class
│   ├── loaders.py            # Loader factory (TXT / PDF / DOCX routing)
│   ├── pdf_loader.py         # PDF document ingestion
│   ├── docx_loader.py        # Word (DOCX) document ingestion
│   └── cleaner.py            # Text cleaning & normalization
│
├── chunking/
│   └── strategies.py         # Fixed-size chunking with overlap
│
├── embeddings/
│   ├── embedder.py           # Embedding abstraction
│   └── cache.py              # Hash-based embedding cache
│
├── vectorstore/
│   └── faiss_store.py        # FAISS index creation & semantic search
│
├── retrieval/
│   └── retriever.py          # Top-K semantic retrieval layer
│
├── llm/
│   └── gemini_llm.py         # Gemini LLM wrapper (Gemini 3 Flash / Pro)
│
├── rag/
│   └── pipeline.py           # End-to-end RAG orchestration
│
├── evaluation/
│   ├── latency.py            # Latency measurement (planned)
│   └── retrieval_metrics.py  # Recall@K, MRR (planned)
│
├── data/
│   ├── raw_docs/             # Ignored (uploaded documents)
│   └── processed_docs/       # Ignored (intermediate artifacts)
│
├── .env
├── config.yaml
├── main.py
├── README.md
└── LICENSE


```

---
## ⚙️ Configuration (`config.yaml`)

All pipeline behavior is controlled via configuration:

- Chunk size & overlap  
- Embedding model selection  
- Vector index parameters  
- Retrieval top-K settings  

This enables **rapid experimentation without changing code**.

---

## 📊 Evaluation & Metrics

Unlike most RAG demos, this project includes an explicit evaluation layer.

Planned / supported metrics:

- Retrieval latency  
- Recall@K  
- Mean Reciprocal Rank (MRR)  
- End-to-end pipeline latency  

---
## 🧪 How to Run Locally

```bash
# Clone repository
git clone https://github.com/Indrasish7/scalable-enterprise-rag.git
cd scalable-enterprise-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python main.py

```

---
## 🧩 Design Philosophy

- Production-first mindset  
- Clear separation of concerns  
- Scales from small document sets to enterprise corpora  
- Easily extensible for hybrid search, reranking, and evaluation  

---
## 🛣️ Roadmap

Planned improvements to evolve this into a fully production-ready RAG system:

- [ ] Hybrid retrieval (BM25 + Dense vectors)
- [ ] Cross-encoder reranking for improved answer relevance
- [ ] Streaming LLM responses
- [ ] Multi-tenant vector index support
- [ ] Monitoring & latency tracing
- [ ] Deployment-ready architecture (Docker / Kubernetes)

---
## 👤 Author

**Indrasish Bhattacharjee**  
AI Engineer | GenAI • RAG • LLMs • FAISS  
📍 India  
🔗 LinkedIn: https://www.linkedin.com/in/indrasishbhattacharjee


---
## 📜 License

This project is licensed under the **MIT License**.
See the `LICENSE` file for details.


---
⭐ If this repository helped you understand **production-grade RAG systems**, consider starring it.
