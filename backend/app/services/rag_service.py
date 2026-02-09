"""
RAG-like similarity retrieval service.
Uses embeddings for similarity search with TF-IDF fallback.
"""
import os
import math
from collections import Counter
from openai import OpenAI


def find_similar_events(event_text: str, past_events: list[dict], top_k: int = 3) -> list[dict]:
    """
    Find similar events using embedding similarity.
    Falls back to TF-IDF if embedding API unavailable.
    
    Args:
        event_text: The query event text
        past_events: List of dicts with 'id' and 'content' keys
        top_k: Number of similar events to return
        
    Returns:
        List of dicts with 'id', 'content', and 'similarity' keys
    """
    if not past_events:
        return []
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            return _find_similar_with_embeddings(event_text, past_events, top_k, api_key)
        except Exception:
            pass
    
    # Fallback to TF-IDF
    return _find_similar_with_tfidf(event_text, past_events, top_k)


def _find_similar_with_embeddings(event_text: str, past_events: list[dict], 
                                   top_k: int, api_key: str) -> list[dict]:
    """Use OpenAI embeddings for similarity search."""
    client = OpenAI(api_key=api_key)
    
    # Get all texts
    texts = [event_text] + [e["content"] for e in past_events]
    
    # Get embeddings
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    
    embeddings = [item.embedding for item in response.data]
    query_embedding = embeddings[0]
    event_embeddings = embeddings[1:]
    
    # Calculate similarities
    similarities = []
    for i, event_emb in enumerate(event_embeddings):
        sim = _cosine_similarity(query_embedding, event_emb)
        similarities.append({
            "id": past_events[i]["id"],
            "content": past_events[i]["content"],
            "similarity": round(sim, 4)
        })
    
    # Sort and return top_k
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_k]


def _find_similar_with_tfidf(event_text: str, past_events: list[dict], 
                              top_k: int) -> list[dict]:
    """Use TF-IDF for similarity search (fallback)."""
    # Tokenize all documents
    all_docs = [event_text] + [e["content"] for e in past_events]
    tokenized = [_tokenize(doc) for doc in all_docs]
    
    # Build vocabulary
    vocab = set()
    for tokens in tokenized:
        vocab.update(tokens)
    vocab = sorted(vocab)
    
    # Calculate IDF
    idf = {}
    n_docs = len(tokenized)
    for term in vocab:
        doc_freq = sum(1 for tokens in tokenized if term in tokens)
        idf[term] = math.log(n_docs / (1 + doc_freq))
    
    # Calculate TF-IDF vectors
    vectors = []
    for tokens in tokenized:
        tf = Counter(tokens)
        vector = [tf.get(term, 0) * idf[term] for term in vocab]
        vectors.append(vector)
    
    query_vector = vectors[0]
    event_vectors = vectors[1:]
    
    # Calculate similarities
    similarities = []
    for i, event_vec in enumerate(event_vectors):
        sim = _cosine_similarity(query_vector, event_vec)
        similarities.append({
            "id": past_events[i]["id"],
            "content": past_events[i]["content"],
            "similarity": round(sim, 4)
        })
    
    # Sort and return top_k
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_k]


def _tokenize(text: str) -> list[str]:
    """Simple tokenization."""
    return text.lower().split()


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)
