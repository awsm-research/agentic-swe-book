"""
MedChat RAG retrieval functions — Chapter 17.

Provides:
  - embed_query()   — embed a query string with OpenAI text-embedding-3-small
  - retrieve()      — cosine similarity search in pgvector
  - rerank()        — cross-encoder reranking with sentence-transformers

Usage:
    from retriever import embed_query, retrieve, rerank

    query_vec = embed_query("First-line treatment for CAP?")
    candidates = retrieve(query_vec, top_k=10)
    top_chunks = rerank("First-line treatment for CAP?", candidates, top_n=3)
    for chunk in top_chunks:
        print(chunk["content"][:200])
"""

from __future__ import annotations

import os
import logging

import psycopg2
import psycopg2.extras
from openai import OpenAI
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Lazily loaded singletons
_openai_client: OpenAI | None = None
_cross_encoder: CrossEncoder | None = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        logger.info(f"Loading cross-encoder model: {RERANK_MODEL}")
        _cross_encoder = CrossEncoder(RERANK_MODEL)
    return _cross_encoder


def _get_connection():
    """Create a psycopg2 connection from DATABASE_URL environment variable."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(url)


# ── Public API ─────────────────────────────────────────────────────────────────


def embed_query(text: str) -> list[float]:
    """
    Embed a query string using OpenAI text-embedding-3-small.

    Args:
        text: The query string to embed.

    Returns:
        A list of 1536 floats representing the embedding vector.
    """
    client = _get_openai_client()
    cleaned = text.replace("\n", " ").strip()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[cleaned])
    return response.data[0].embedding


def retrieve(
    query: str,
    top_k: int = 5,
    source_type: str | None = None,
) -> list[dict]:
    """
    Retrieve the top-k most similar chunks from pgvector.

    Args:
        query:       The user's question (will be embedded internally).
        top_k:       Maximum number of chunks to return.
        source_type: Optional filter — restrict results to a specific document
                     source type, e.g. 'markdown' or 'csv'.

    Returns:
        List of dicts with keys: id, content, chunk_index, similarity,
        metadata, document_id, title, source_type.
    """
    query_vec = embed_query(query)
    # Serialise the vector as a PostgreSQL-compatible string
    vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

    conn = _get_connection()
    try:
        if source_type:
            sql = """
                SELECT
                    c.id,
                    c.content,
                    c.chunk_index,
                    c.metadata,
                    d.id            AS document_id,
                    d.title,
                    d.source_type,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE d.source_type = %s
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
            """
            params = (vec_str, source_type, vec_str, top_k)
        else:
            sql = """
                SELECT
                    c.id,
                    c.content,
                    c.chunk_index,
                    c.metadata,
                    d.id            AS document_id,
                    d.title,
                    d.source_type,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
            """
            params = (vec_str, vec_str, top_k)

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


def rerank(
    query: str,
    chunks: list[dict],
    top_n: int = 3,
) -> list[dict]:
    """
    Re-rank retrieved chunks using a cross-encoder model.

    Scores each (query, chunk) pair with a cross-encoder and returns the
    top_n most relevant chunks in descending relevance order.

    Args:
        query:   The original user question.
        chunks:  List of chunk dicts as returned by ``retrieve()``.
        top_n:   Number of chunks to return after reranking.

    Returns:
        Sorted list of chunk dicts with an added 'reranker_score' field.
        The list is ordered from highest to lowest relevance.
    """
    if not chunks:
        return []

    model = _get_cross_encoder()
    pairs = [(query, ch["content"]) for ch in chunks]
    scores = model.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["reranker_score"] = float(score)

    reranked = sorted(chunks, key=lambda c: c["reranker_score"], reverse=True)
    return reranked[:top_n]
