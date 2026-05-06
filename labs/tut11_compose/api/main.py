# api/main.py
"""Minimal bookshop API: list and add books."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "bookshop")
DB_NAME = os.getenv("DB_NAME", "bookshop")
DB_PASSWORD_FILE = os.getenv("DB_PASSWORD_FILE", "/run/secrets/db_password")
APP_VERSION = os.getenv("APP_VERSION", "0.0.0+local")


def read_password() -> str:
    return Path(DB_PASSWORD_FILE).read_text().strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=read_password(), database=DB_NAME,
        min_size=1, max_size=5,
    )
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id    SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
            """
        )
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


class Book(BaseModel):
    title: str
    author: str


@app.get("/healthz")
async def healthz():
    try:
        async with app.state.pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok", "version": APP_VERSION}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"db unreachable: {exc}")


@app.get("/books")
async def list_books():
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, title, author FROM books ORDER BY id")
    return [dict(r) for r in rows]


@app.post("/books", status_code=201)
async def add_book(book: Book):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO books (title, author) VALUES ($1, $2) RETURNING id",
            book.title, book.author,
        )
    return {"id": row["id"], **book.model_dump()}
