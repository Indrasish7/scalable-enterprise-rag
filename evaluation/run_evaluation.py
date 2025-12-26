from evaluation.latency import measure_latency
from evaluation.retrieval_metrics import recall_at_k


def evaluate_retrieval(
    pipeline,
    query: str,
    relevant_doc_ids: list,
    k: int = 5
) -> dict:
    """
    Run retrieval evaluation for a single query.
    """

    # Measure retrieval latency
    retrieval_stats = measure_latency(
        pipeline.retriever.retrieve,
        query,
        top_k=k
    )

    retrieved_chunks = retrieval_stats["result"]

    retrieved_parent_ids = [
        chunk["metadata"]["parent_doc_id"]
        for chunk in retrieved_chunks
        if chunk.get("metadata") and "parent_doc_id" in chunk["metadata"]
    ]

    recall = recall_at_k(
        retrieved_ids=retrieved_parent_ids,
        relevant_ids=relevant_doc_ids,
        k=k
    )

    return {
        "query": query,
        "recall@k": recall,
        "retrieval_latency_ms": retrieval_stats["latency_ms"],
        "num_retrieved_chunks": len(retrieved_chunks)
    }
