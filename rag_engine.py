import json
import os

import faiss
from sentence_transformers import SentenceTransformer

INDEX_DIR = "vector_db"
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
LABELS_PATH = os.path.join(INDEX_DIR, "labels.txt")
DOCS_PATH = os.path.join(INDEX_DIR, "docs.json")

MAX_CONTEXT_CHARS = 2400
SEARCH_POOL = 32

model = SentenceTransformer("all-MiniLM-L6-v2")

def ensure_index_exists():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(LABELS_PATH) or not os.path.exists(DOCS_PATH):
        from build_index import build_index
        build_index()

ensure_index_exists()

index = faiss.read_index(INDEX_PATH)

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels = f.read().splitlines()

with open(DOCS_PATH, "r", encoding="utf-8") as f:
    docs: list[str] = json.load(f)


def _normalize_persona(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def _label_matches(label: str, persona: str | None, subpersona: str | None) -> bool:
    if persona and f"persona={persona}" not in label:
        return False
    if subpersona and f"subpersona={subpersona}" not in label:
        return False
    return True


def retrieve_context(
    query: str,
    top_k: int = 3,
    persona: str | None = None,
    subpersona: str | None = None,
) -> list[str]:
    """
    Retrieve top-k text chunks for the query, optionally filtered by persona/subpersona.
    """
    persona_key = _normalize_persona(persona)
    subpersona_key = _normalize_persona(subpersona)

    k = min(max(top_k * 8, top_k), index.ntotal, SEARCH_POOL)
    query_vec = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = index.search(query_vec, k)

    ranked: list[tuple[float, str]] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        label = labels[idx]
        if persona_key or subpersona_key:
            if not _label_matches(label, persona_key, subpersona_key):
                continue
        ranked.append((float(score), docs[idx]))

    if not ranked and (persona_key or subpersona_key):
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            ranked.append((float(score), docs[idx]))

    seen: set[str] = set()
    results: list[str] = []
    total_chars = 0

    for _, text in sorted(ranked, key=lambda item: item[0], reverse=True):
        snippet = text.strip()
        if not snippet or snippet in seen:
            continue
        seen.add(snippet)
        if total_chars + len(snippet) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total_chars
            if remaining <= 0:
                break
            snippet = snippet[:remaining].rstrip() + "…"
        results.append(snippet)
        total_chars += len(snippet)
        if len(results) >= top_k:
            break

    return results
