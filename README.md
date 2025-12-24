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
│   └── ui.py
│
├── data/
│   ├── raw_docs/
│   └── processed_docs/
│
├── ingestion/
│   ├── loaders.py
│   └── cleaner.py
│
├── chunking/
│   └── strategies.py
│
├── embeddings/
│   ├── embedder.py
│   └── cache.py
│
├── vectorstore/
│   └── faiss_store.py
│
├── retrieval/
│   └── retriever.py
│
├── llm/
│   └── gemini_llm.py
│
├── rag/
│   └── pipeline.py
│
├── evaluation/
│   ├── latency.py
│   └── retrieval_metrics.py
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
