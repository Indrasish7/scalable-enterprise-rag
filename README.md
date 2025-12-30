# 🧠 Scalable Enterprise RAG System

**Production-grade Retrieval-Augmented Generation (RAG) system** designed for enterprise-scale document ingestion, semantic search, and LLM-powered question answering.

This project focuses on **scalability, modularity, system design, observability, and evaluation** — not demo-level RAG pipelines.

---

## 🚀 Key Features

- Modular **end-to-end RAG architecture**
- **Multi-format document ingestion** (TXT, PDF, DOCX)
- **Incremental knowledge base updates** (no re-embedding unchanged data)
- **Persistent FAISS vector store**
- Hash-based **embedding cache**
- **Observability-first UI** (latency, retrieved chunks, confidence)
- Explicit **evaluation layer** (Recall@K, latency)
- **Dockerized & Cloud Run–ready**
- **GCP Secret Manager integration**
- Designed with **enterprise document systems** in mind

---

## 🌐 Live Deployment

The application is deployed on **Google Cloud Run** and is publicly accessible.

🔗 **Live URL:**  
https://scalable-enterprise-rag-761523979642.asia-south1.run.app

### Deployment Details
- Hosted on **Google Cloud Run**
- Container image stored in **Artifact Registry**
- HTTPS enabled by default
- Autoscaling based on traffic
- Secrets securely injected via **GCP Secret Manager**

> This deployment closely mirrors how production-grade GenAI / RAG services are deployed in real enterprise environments.

---

## 📄 Supported Document Formats

The system supports **multi-format enterprise document ingestion**:

- ✅ **TXT** — Plain text files  
- ✅ **PDF** — Extracted using `pypdf`  
- ✅ **DOCX** — Extracted using `python-docx`

Documents are routed to loaders using a **factory-based ingestion layer**, making it trivial to add support for formats like HTML, Markdown, or PPTX.

---

## 🧠 Knowledge Base Lifecycle

This system implements a **production-grade knowledge base lifecycle**.

### ✅ Incremental Ingestion
- Each document receives a **stable, deterministic document ID**
- Content hashes tracked via `kb_state.json`
- **Only new or modified documents are chunked and embedded**

### ✅ Persistent Vector Store
- FAISS index and metadata are persisted
- Restarting the service **does not rebuild embeddings**
- The knowledge base grows incrementally over time

### ✅ Safe Reuse Without Recompute
- If documents are already ingested, the system **reuses the existing FAISS index**
- The RAG pipeline auto-initializes from persisted state
- This avoids unnecessary compute cost and LLM calls

---

## 👀 Observability & Transparency

The Streamlit UI exposes internal system behavior:

- ⏱ **Retrieval latency (ms)**
- 📦 **Number of retrieved chunks**
- 🟢 **Confidence indicator** (heuristic)
- 📚 **Exact retrieved contexts used by the LLM**

This mirrors **internal enterprise RAG tools** used at large tech companies — not black-box demos.

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
│   ├── embedder.py           # GeminiEmbedder
│   └── cache.py              # Hash-based embedding cache
│
├── vectorstore/
│   ├── faiss_store.py        # Persistent FAISS index wrapper
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
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE

```

---
## ⚙️ Configuration & Secrets

### Local Development
- Secrets are loaded via a `.env` file  
- The `.env` file is **gitignored**

### Production (Cloud Run)
- Secrets are managed using **GCP Secret Manager**
- Secrets are **injected as environment variables at runtime**
- **No secrets are baked** into Docker images or source code

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
streamlit run app/ui.py

```
---
## 🐳 Docker (Production-Equivalent)

```bash
docker build -t scalable-enterprise-rag .
docker run -p 8501:8501 scalable-enterprise-rag
```
---
## ☁️ Cloud Deployment (GCP)

- Docker image pushed to **Artifact Registry**
- Deployed on **Cloud Run**
- **Autoscaling** enabled by default
- Secure **HTTPS endpoint** exposed
- Secrets injected securely via **GCP Secret Manager**

This setup mirrors **real-world GenAI service deployments** used in production environments.

---
## 🧩 Design Philosophy

- Production-first mindset  
- Clear separation of concerns
- Compute-efficient incremental updates
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
- [ ]  Kubernetes-native deployment

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
