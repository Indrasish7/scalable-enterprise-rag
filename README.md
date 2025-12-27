# 🧠 Scalable Enterprise RAG System

**Production-grade Retrieval-Augmented Generation (RAG) system** designed for enterprise-scale document ingestion, semantic search, and LLM-powered question answering.

This project focuses on **scalability, modularity, system design, and evaluation**, not just demo-level RAG pipelines.

---

## 🚀 Key Features

- Modular **end-to-end RAG architecture**
- **Multi-format document ingestion** (TXT, PDF, DOCX)
- **Incremental knowledge base updates** (no re-embedding unchanged data)
- **Persistent FAISS vector store**
- Hash-based **embedding cache**
- **Observability-first UI** (latency, retrieved chunks, confidence)
- Explicit **evaluation layer** (Recall@K, latency)
- Designed with **enterprise document systems** in mind

---

## 📄 Supported Document Formats

The system supports **multi-format enterprise document ingestion**:

- ✅ **TXT** — Plain text files  
- ✅ **PDF** — Extracted using `pypdf`  
- ✅ **DOCX** — Extracted using `python-docx`

- Multi-format ingestion (TXT, PDF, DOCX) via extensible loader architecture


Documents are automatically routed to the correct loader using a **factory-based ingestion layer**, making it easy to extend support to additional formats such as HTML, Markdown, or PPTX.

---

## 🧠 Knowledge Base Lifecycle

This system implements a **production-grade knowledge base lifecycle**.

### ✅ Incremental Ingestion
- Each document is assigned a **stable, deterministic document ID**
- Content hashes are tracked via `kb_state.json`
- **Only new or modified documents are re-chunked and re-embedded**

### ✅ Persistent Vector Store
- FAISS index and metadata are persisted locally
- Restarting the app **does NOT rebuild embeddings**
- The KB grows incrementally over time

### ✅ Ignored Runtime Data
The following artifacts are **intentionally excluded from Git**:

- FAISS index files
- KB state (`kb_state.json`)
- Metadata (`metadata.pkl`)
- Uploaded documents

> This mirrors real production systems where data lives in object storage, volumes, or databases — not Git.

---

## 👀 Observability & Transparency

The Streamlit UI exposes internal system behavior:

- ⏱ **Retrieval latency (ms)**
- 📦 **Number of retrieved chunks**
- 🟢 **Confidence indicator** (heuristic)
- 📚 **Exact retrieved contexts used by the LLM**

This makes the system feel like an **internal Google / Meta RAG tool**, not a black box.

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
│ Embeddings    │ ← GeminiEmbedder + cache
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Vector Store  │ ← FAISS (persistent)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Retrieval     │ ← Top-K semantic search
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LLM Response  │ ← Gemini (grounded)
└──────────────┘
```
---

## 📁 Project Structure
```text

scalable-enterprise-rag/
│
├── app/
│   └── ui.py                 # Streamlit UI (ingestion, QA, observability)
│
├── ingestion/
│   ├── base.py               # BaseLoader abstraction
│   ├── loaders.py            # Loader factory (TXT / PDF / DOCX)
│   ├── pdf_loader.py
│   ├── docx_loader.py
│   └── cleaner.py
│
├── chunking/
│   └── strategies.py         # Fixed-size chunking with overlap
│
├── embeddings/
│   ├── embedder.py           # GeminiEmbedder / DummyEmbedder
│   └── cache.py              # Hash-based embedding cache
│
├── vectorstore/
│   ├── faiss_store.py        # FAISS index wrapper
│   └── kb_manager.py         # Incremental KB lifecycle manager
│
├── retrieval/
│   └── retriever.py
│
├── llm/
│   └── gemini_llm.py
│
├── rag/
│   └── pipeline.py           # RAG orchestration + observability
│
├── evaluation/
│   ├── latency.py
│   ├── retrieval_metrics.py
│   └── run_evaluation.py
│
├── data/                     # ❌ Ignored (runtime artifacts)
│
├── .gitignore
├── .env                      # GEMINI_API_KEY (ignored)
├── README.md
└── LICENSE

```

---
## ⚙️ Configuration & Secrets

- API keys are loaded from `.env`
- `.env` and all runtime data are **gitignored**

### Production Deployment Recommendations

For production environments, secrets and state should be managed using:

- Environment variables
- Secret managers (e.g., AWS Secrets Manager, GCP Secret Manager)
- Persistent volumes or object storage (e.g., EBS, GCS, S3)

---

## 📊 Evaluation & Metrics

Unlike most RAG demos, this project includes an explicit evaluation layer.

Planned/supported metrics:

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
