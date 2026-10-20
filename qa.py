"""Shared retrieval based question answering for the PEOPLE dataset."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re

import numpy as np
from fastembed import TextEmbedding


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DATA_PATH = Path(__file__).resolve().parents[2] / "people.sql"
INSERT_ROW = re.compile(
    r"\('((?:''|[^'])*)',\s*'((?:''|[^'])*)',\s*'\[([^\]]+)\]'::vector\)"
)


@lru_cache(maxsize=1)
def _load_index() -> tuple[list[dict[str, str]], np.ndarray, TextEmbedding]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"找不到資料檔：{DATA_PATH}")

    sql = DATA_PATH.read_text(encoding="utf-8")
    records: list[dict[str, str]] = []
    embeddings: list[list[float]] = []
    for match in INSERT_ROW.finditer(sql):
        name, people, vector_text = match.groups()
        name = name.replace("''", "'").strip()
        people = people.replace("''", "'").strip()
        vector = [float(value) for value in vector_text.split(",")]
        if len(vector) != 384:
            raise ValueError(f"people.sql 中的向量維度不是 384：{name}")
        if name and people:
            records.append({"name": name, "people": people})
            embeddings.append(vector)
    if not records:
        raise ValueError("people.sql 沒有可解析的人物資料與向量。")

    embedder = TextEmbedding(model_name=MODEL_NAME)
    vectors = np.asarray(embeddings, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / np.maximum(norms, 1e-12)
    return records, vectors, embedder


def answer_question(question: str) -> str:
    """Return the most relevant people records for a user's question."""
    question = (question or "").strip()
    if not question:
        return "請輸入問題，例如：李姓有哪些人物？"

    records, vectors, embedder = _load_index()
    query_vector = np.asarray(
        next(embedder.query_embed(question)), dtype=np.float32
    )
    query_vector /= max(float(np.linalg.norm(query_vector)), 1e-12)
    scores = vectors @ query_vector

    # Prefer a directly named surname or person when the question names one.
    direct_matches: list[int] = []
    for index, record in enumerate(records):
        person_name = record["people"].split("：", 1)[0]
        if (
            record["name"] + "姓" in question
            or "姓" + record["name"] in question
            or person_name in question
        ):
            direct_matches.append(index)

    if direct_matches:
        ranked = sorted(direct_matches, key=lambda i: float(scores[i]), reverse=True)
        chosen = ranked[:5]
    else:
        chosen = np.argsort(scores)[::-1][:3].tolist()
        if not chosen or float(scores[chosen[0]]) < 0.15:
            return "在目前的人物資料中找不到足夠相關的內容，請試著改問某個姓氏或人物。"

    lines = ["根據 PEOPLE 資料集，相關人物如下："]
    for index in chosen:
        row = records[index]
        lines.append(f"- **{row['people']}**")
    lines.append("\n回答內容依據 people.sql 的資料與向量；資料未涵蓋的細節不會另外推測。")
    return "\n".join(lines)


def get_examples() -> list[list[str]]:
    records, _, _ = _load_index()
    if not records:
        return []
    examples = [f"{row['name']}姓有哪些人物？" for row in records[:5]]
    return [[example] for example in examples]

