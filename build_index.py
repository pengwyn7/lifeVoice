import json
import os
import re

import faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = "data"
INDEX_DIR = "vector_db"
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
LABELS_PATH = os.path.join(INDEX_DIR, "labels.txt")
DOCS_PATH = os.path.join(INDEX_DIR, "docs.json")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

PERSONA_MAP = {
    "professional.txt": ("professional", None),
    "family.txt": ("family", None),
    "friend.txt": ("friend", ["optimist", "pessimist", "jejemon", "youngstunna", "brainrot"]),
    "random.txt": ("random", None),
    "you.txt": ("you", None),
}


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip() if current else para
            continue
        if current:
            chunks.append(current)
        if len(para) <= chunk_size:
            current = para
            continue
        start = 0
        while start < len(para):
            piece = para[start : start + chunk_size]
            chunks.append(piece)
            start += chunk_size - overlap
        current = ""

    if current:
        chunks.append(current)

    if not chunks:
        return [text[:chunk_size]]
    return chunks


def split_friend_sections(text: str) -> dict[str, str]:
    parts = re.split(r"--- (\w+) Friend ---", text)
    sections: dict[str, str] = {}
    for i in range(1, len(parts), 2):
        name = parts[i].strip().lower()
        sections[name] = parts[i + 1].strip()
    return sections


def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    docs: list[str] = []
    labels: list[str] = []

    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        persona, subpersonas = PERSONA_MAP.get(filename, ("general", None))

        if subpersonas:
            sections = split_friend_sections(text)
            for sub in subpersonas:
                section = sections.get(sub, "").strip()
                if not section:
                    continue
                for chunk in chunk_text(section):
                    docs.append(chunk)
                    labels.append(f"{filename} | persona={persona} | subpersona={sub}")
        else:
            for chunk in chunk_text(text):
                docs.append(chunk)
                labels.append(f"{filename} | persona={persona}")

    if not docs:
        raise RuntimeError("No documents found in data/ — cannot build index.")

    embeddings = model.encode(docs, normalize_embeddings=True)
    embeddings = embeddings.astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(labels))
    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)

    print(f"Index built with {len(docs)} chunks across {len(set(labels))} label groups.")


if __name__ == "__main__":
    build_index()
