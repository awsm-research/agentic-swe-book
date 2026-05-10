"""
MedChat document ingestion pipeline — Chapter 17.

Loads Markdown, CSV, and text files from a docs/ directory, chunks them
with RecursiveCharacterTextSplitter, embeds each chunk with OpenAI
text-embedding-3-small, and stores the results in pgvector via psycopg2.

Usage:
    export DATABASE_URL="postgresql://user:pass@localhost/medchat"
    export OPENAI_API_KEY="sk-..."
    python ingest.py                  # ingests docs/ by default
    python ingest.py path/to/docs     # ingests a custom directory
"""

import os
import sys
import csv
import time
import logging
from pathlib import Path

import psycopg2
import psycopg2.extras
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("medchat.ingest")

DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 512      # tokens approximated by character count (~4 chars/token)
CHUNK_OVERLAP = 50
EMBED_BATCH_SIZE = 100


# ── Database helpers ───────────────────────────────────────────────────────────


def get_connection():
    """Return a psycopg2 connection using DATABASE_URL from the environment."""
    url = os.environ.get("DATABASE_URL", DATABASE_URL)
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(url)


def ensure_schema(conn) -> None:
    """Create tables and index if they don't already exist."""
    sql = """
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS documents (
        id          SERIAL PRIMARY KEY,
        title       TEXT NOT NULL,
        source_type TEXT NOT NULL,
        file_path   TEXT NOT NULL,
        ingested_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS chunks (
        id          BIGSERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
        content     TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        embedding   vector(1536),
        metadata    JSONB DEFAULT '{}'
    );

    CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    logger.info("Schema ensured.")


def upsert_document(conn, title: str, source_type: str, file_path: str) -> int:
    """Insert or update a document record. Returns the document id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (title, source_type, file_path)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            (title, source_type, str(file_path)),
        )
        row = cur.fetchone()
        if row is None:
            # Row already existed — fetch its id
            cur.execute(
                "SELECT id FROM documents WHERE file_path = %s",
                (str(file_path),),
            )
            row = cur.fetchone()
    conn.commit()
    return row[0]


def delete_chunks_for_document(conn, document_id: int) -> None:
    """Remove existing chunks before re-ingestion."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
    conn.commit()


def insert_chunks(conn, document_id: int, chunks: list[dict]) -> None:
    """Batch-insert chunk rows (content + embedding + metadata)."""
    if not chunks:
        return
    records = [
        (
            document_id,
            ch["chunk_index"],
            ch["content"],
            ch["embedding"],  # list[float] — psycopg2 + pgvector accepts this
            psycopg2.extras.Json(ch.get("metadata", {})),
        )
        for ch in chunks
    ]
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO chunks (document_id, chunk_index, content, embedding, metadata)
            VALUES %s
            """,
            records,
            template="(%s, %s, %s, %s::vector, %s)",
        )
    conn.commit()


# ── Text loading helpers ───────────────────────────────────────────────────────


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_csv_as_text(path: Path) -> str:
    """Convert each CSV row into a readable natural-language paragraph."""
    lines: list[str] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            parts = [f"{k}: {v}" for k, v in row.items() if v]
            lines.append(" | ".join(parts))
    return "\n\n".join(lines)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Chunking ───────────────────────────────────────────────────────────────────


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks using LangChain's splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE * 4,    # approximate character budget (~4 chars/token)
        chunk_overlap=CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


# ── Embedding ──────────────────────────────────────────────────────────────────


def embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts and return a list of float vectors."""
    cleaned = [t.replace("\n", " ").strip() for t in texts]
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=cleaned)
    return [item.embedding for item in response.data]


def embed_all(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Embed texts in batches, respecting the API rate limit."""
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i : i + EMBED_BATCH_SIZE]
        all_embeddings.extend(embed_batch(client, batch))
        if i + EMBED_BATCH_SIZE < len(texts):
            time.sleep(0.1)  # modest throttle between batches
    return all_embeddings


# ── Single-document ingestion ─────────────────────────────────────────────────


def ingest_file(path: Path, client: OpenAI, conn) -> int:
    """
    Ingest one file: load → chunk → embed → store.

    Returns the number of chunks stored.
    """
    suffix = path.suffix.lower()
    title = path.stem.replace("_", " ").title()

    if suffix in {".md", ".markdown"}:
        source_type = "markdown"
        text = load_markdown(path)
    elif suffix == ".csv":
        source_type = "csv"
        text = load_csv_as_text(path)
    elif suffix in {".txt", ".text"}:
        source_type = "text"
        text = load_text(path)
    else:
        logger.warning(f"Skipping unsupported file type: {path.name}")
        return 0

    raw_chunks = chunk_text(text)
    if not raw_chunks:
        logger.warning(f"No chunks produced from {path.name}")
        return 0

    logger.info(f"Embedding {len(raw_chunks)} chunks from {path.name} …")
    embeddings = embed_all(client, raw_chunks)

    doc_id = upsert_document(conn, title=title, source_type=source_type, file_path=path)
    delete_chunks_for_document(conn, doc_id)

    chunk_records = [
        {
            "chunk_index": i,
            "content": text_chunk,
            "embedding": emb,
            "metadata": {"source_file": path.name, "source_type": source_type},
        }
        for i, (text_chunk, emb) in enumerate(zip(raw_chunks, embeddings))
    ]
    insert_chunks(conn, doc_id, chunk_records)

    logger.info(f"  → Stored {len(chunk_records)} chunks from {path.name}")
    return len(chunk_records)


# ── Corpus ingestion ───────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".md", ".markdown", ".csv", ".txt", ".text"}


def ingest_all_docs(docs_dir: str) -> None:
    """
    Ingest all supported files in *docs_dir* into pgvector.

    Args:
        docs_dir: Path to the directory containing source documents.
    """
    docs_path = Path(docs_dir)
    if not docs_path.is_dir():
        logger.error(f"Directory not found: {docs_path}")
        sys.exit(1)

    client = OpenAI()
    conn = get_connection()
    ensure_schema(conn)

    total_chunks = 0
    files = sorted(
        f for f in docs_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        logger.warning(f"No supported files found in {docs_path}")
        return

    for file_path in files:
        try:
            n = ingest_file(file_path, client, conn)
            total_chunks += n
        except Exception as exc:
            logger.error(f"Failed to ingest {file_path.name}: {exc}")

    conn.close()
    logger.info(
        f"Ingestion complete. {len(files)} file(s) processed, "
        f"{total_chunks} total chunks stored."
    )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    docs_directory = sys.argv[1] if len(sys.argv) > 1 else "docs"
    ingest_all_docs(docs_directory)
