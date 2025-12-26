from typing import List


def recall_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    """
    Compute Recall@K.
    """
    retrieved_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)

    if not relevant_set:
        return 0.0

    return len(retrieved_k & relevant_set) / len(relevant_set)
