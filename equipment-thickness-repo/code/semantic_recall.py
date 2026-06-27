#!/usr/bin/env python3
"""Semantic Memory Recall v1.0 (Phase 4 Codex 30-day sprint).

Indexes learned.md + shared/lessons.jsonl + project-local reports into a
searchable index. Provides 3 query modes:
  - keyword:    BM25-style token overlap scoring
  - semantic:   embedding-free cosine on keyword presence vectors
  - hybrid:     weighted combination of keyword + semantic + recency

Recall quality target: top-5 results include the relevant lesson
(matched against human-curated ground truth eval cases).

Usage:
    semantic_recall.py build-index
    semantic_recall.py query "DGM misevolution attack surface" --mode hybrid --top 5
    semantic_recall.py query "..." --mode keyword --top 10
    semantic_recall.py query "..." --mode semantic --top 5
    semantic_recall.py eval [--limit 20]
    semantic_recall.py stats

This is Phase 4 v1.0: lightweight index (no embedding model required).
For Phase 4 v2.0 we plan to add embedding-based recall (sentence-transformers
local) and FAISS indexing.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


MEMPALACE = Path.home() / ".mempalace"
KIMI_DIR = MEMPALACE / "agents" / "kimi"
SHARED_DIR = MEMPALACE / "agents" / "shared"
INDEX_PATH = MEMPALACE / "agents" / "shared" / "semantic_recall_index.json"
EVAL_PATH = Path(__file__).parent.parent / "evals" / "semantic_recall_eval.jsonl"


@dataclass
class IndexedChunk:
    chunk_id: str
    source: str
    source_path: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    importance: str = "medium"
    ts: str = ""
    token_freq: dict[str, int] = field(default_factory=dict)
    doc_length: int = 0


@dataclass
class RecallResult:
    chunk_id: str
    title: str
    source: str
    score: float
    snippet: str
    matched_terms: list[str] = field(default_factory=list)


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]+|[\u4e00-\u9fff]+")
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "of", "in", "to",
    "for", "on", "with", "at", "by", "from", "as", "and", "or", "but",
    "not", "no", "if", "then", "else", "when", "where", "how", "why",
    "what", "which", "this", "that", "these", "those", "it", "its",
    "的", "了", "是", "在", "我", "你", "他", "她", "它", "我们",
    "你们", "他们", "和", "与", "或", "但", "不", "也", "都",
}


def tokenize(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) >= 2]


def chunk_learned_md(path: Path) -> list[IndexedChunk]:
    chunks = []
    if not path.exists():
        return chunks
    content = path.read_text()
    sections = re.split(r"\n(?=##\s)", content)
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        lines = section.strip().split("\n", 1)
        title = lines[0].lstrip("#").strip() if lines else f"section_{i}"
        body = lines[1] if len(lines) > 1 else ""
        tokens = tokenize(section)
        chunks.append(IndexedChunk(
            chunk_id=f"learned.md::{title[:50]}",
            source="learned.md",
            source_path=str(path),
            title=title,
            content=body[:500],
            tags=["kimi", "learned"],
            importance="high",
            ts="",
            token_freq=dict(Counter(tokens)),
            doc_length=len(tokens),
        ))
    return chunks


def chunk_lessons_jsonl(path: Path) -> list[IndexedChunk]:
    chunks = []
    if not path.exists():
        return chunks
    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = f"{entry.get('task', '')} {entry.get('critique', '')}"
            tokens = tokenize(content)
            chunks.append(IndexedChunk(
                chunk_id=f"lessons.jsonl::{entry.get('lesson_id', f'line_{i}')}",
                source="lessons.jsonl",
                source_path=str(path),
                title=entry.get("task", "")[:80],
                content=entry.get("critique", "")[:500],
                tags=entry.get("tags", []),
                importance=entry.get("importance", "medium"),
                ts=entry.get("ts", ""),
                token_freq=dict(Counter(tokens)),
                doc_length=len(tokens),
            ))
    return chunks


def chunk_project_reports(eval_history_dir: Path) -> list[IndexedChunk]:
    chunks = []
    if not eval_history_dir.exists():
        return chunks
    for md_file in eval_history_dir.glob("*.md"):
        content = md_file.read_text()
        tokens = tokenize(content)
        chunks.append(IndexedChunk(
            chunk_id=f"report::{md_file.name}",
            source="report",
            source_path=str(md_file),
            title=md_file.stem,
            content=content[:500],
            tags=["report", "weekly"],
            importance="medium",
            ts="",
            token_freq=dict(Counter(tokens)),
            doc_length=len(tokens),
        ))
    return chunks


def build_index() -> list[IndexedChunk]:
    chunks = []
    chunks.extend(chunk_learned_md(KIMI_DIR / "learned.md"))
    chunks.extend(chunk_lessons_jsonl(SHARED_DIR / "lessons.jsonl"))
    project_reports = Path(__file__).parent.parent.parent / "07-reports" / "eval-history"
    chunks.extend(chunk_project_reports(project_reports))
    return chunks


def compute_idf(chunks: list[IndexedChunk]) -> dict[str, float]:
    """Compute inverse document frequency for each term across the corpus.

    IDF(t) = log(N / df(t)) where df(t) is the number of chunks containing t.
    Rare terms get higher IDF; common terms get lower.
    """
    df: dict[str, int] = {}
    for c in chunks:
        for term in set(c.token_freq.keys()):
            df[term] = df.get(term, 0) + 1
    n = len(chunks)
    return {term: math.log((n + 1) / (freq + 1)) + 1 for term, freq in df.items()}


def save_index(chunks: list[IndexedChunk]) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump([asdict(c) for c in chunks], f, ensure_ascii=False, indent=2)


def load_index() -> list[IndexedChunk]:
    if not INDEX_PATH.exists():
        return []
    with open(INDEX_PATH) as f:
        data = json.load(f)
    return [IndexedChunk(**c) for c in data]


def score_keyword(query_tokens: list[str], chunk: IndexedChunk,
                  idf: dict[str, float] | None = None) -> float:
    if chunk.doc_length == 0:
        return 0.0
    score = 0.0
    for qt in query_tokens:
        tf = chunk.token_freq.get(qt, 0)
        if tf > 0:
            idf_weight = idf.get(qt, 1.0) if idf else 1.0
            score += (tf / (tf + 1.5)) * idf_weight * (len(qt) / 10.0)
    return score / math.sqrt(chunk.doc_length)


def score_semantic(query_tokens: list[str], all_chunks: list[IndexedChunk],
                   chunk: IndexedChunk) -> float:
    if not all_chunks or chunk.doc_length == 0:
        return 0.0
    vocab = set(query_tokens)
    for tok in chunk.token_freq:
        vocab.add(tok)
    q_vec = [1 if t in query_tokens else 0 for t in vocab]
    c_vec = [1 if chunk.token_freq.get(t, 0) > 0 else 0 for t in vocab]
    dot = sum(a * b for a, b in zip(q_vec, c_vec))
    q_norm = math.sqrt(sum(x * x for x in q_vec))
    c_norm = math.sqrt(sum(x * x for x in c_vec))
    if q_norm == 0 or c_norm == 0:
        return 0.0
    return dot / (q_norm * c_norm)


def score_hybrid(query_tokens: list[str], all_chunks: list[IndexedChunk],
                 chunk: IndexedChunk, idf: dict[str, float] | None = None) -> float:
    kw = score_keyword(query_tokens, chunk, idf=idf)
    sem = score_semantic(query_tokens, all_chunks, chunk)
    # Drop importance weight — it was over-amplifying common "high" importance
    # entries (e.g., routine safety rules) over contextually relevant ones.
    return 0.7 * kw + 0.3 * sem


def recall(query: str, chunks: list[IndexedChunk],
           mode: str = "hybrid", top: int = 5) -> list[RecallResult]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    idf = compute_idf(chunks) if chunks else {}

    if mode == "keyword":
        scored = [(score_keyword(query_tokens, c, idf=idf), c) for c in chunks]
    elif mode == "semantic":
        scored = [(score_semantic(query_tokens, chunks, c), c) for c in chunks]
    elif mode == "hybrid":
        scored = [(score_hybrid(query_tokens, chunks, c, idf=idf), c) for c in chunks]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    scored.sort(key=lambda x: -x[0])
    results = []
    for score, chunk in scored[:top]:
        if score <= 0:
            break
        matched = [t for t in query_tokens if chunk.token_freq.get(t, 0) > 0]
        snippet = chunk.content[:200].replace("\n", " ").strip()
        results.append(RecallResult(
            chunk_id=chunk.chunk_id,
            title=chunk.title,
            source=chunk.source,
            score=round(score, 4),
            snippet=snippet,
            matched_terms=matched[:10],
        ))
    return results


EVAL_CASES = [
    {"case_id": "SR-001", "query": "DGM self-modifying agent safety",
     "expected_source": "lessons.jsonl", "expected_keywords": ["dgm", "self-modifying"]},
    {"case_id": "SR-002", "query": "MLAS 25 attack surface critical",
     "expected_source": "learned.md", "expected_keywords": ["mlas", "attack"]},
    {"case_id": "SR-003", "query": "agent silent failure entropy principle",
     "expected_source": "lessons.jsonl", "expected_keywords": ["silent", "failure"]},
    {"case_id": "SR-004", "query": "ICA model layer architecture 6 layers",
     "expected_source": "learned.md", "expected_keywords": ["ica", "layer"]},
    {"case_id": "SR-005", "query": "Kimi Code CLI tool truncation M3",
     "expected_source": "lessons.jsonl", "expected_keywords": ["kimi", "cli", "truncation"]},
    {"case_id": "SR-006", "query": "anthropic teaching claude why misalignment",
     "expected_source": "learned.md", "expected_keywords": ["anthropic", "claude", "why"]},
    {"case_id": "SR-007", "query": "skillDAG typed dependency 12.8 percent",
     "expected_source": "lessons.jsonl", "expected_keywords": ["skilldag", "12.8"]},
    {"case_id": "SR-008", "query": "NEXUS 5 bridge governance outcome",
     "expected_source": "lessons.jsonl", "expected_keywords": ["nexus", "5", "bridge"]},
    {"case_id": "SR-009", "query": "装备率量化协议 kappa inter-rater",
     "expected_source": "learned.md", "expected_keywords": ["装备率", "kappa"]},
    {"case_id": "SR-010", "query": "Phase 6 weekly eval harness scoreboard",
     "expected_source": "report", "expected_keywords": ["weekly", "eval", "scoreboard"]},
    {"case_id": "SR-011", "query": "CADVP v1.1 channel fracture 13 dimensions",
     "expected_source": "lessons.jsonl", "expected_keywords": ["cadvp", "13"]},
    {"case_id": "SR-012", "query": "misevolution stuck evolving agents",
     "expected_source": "lessons.jsonl", "expected_keywords": ["misevolution"]},
    {"case_id": "SR-013", "query": "DCPM dual process memory sleep-time",
     "expected_source": "lessons.jsonl", "expected_keywords": ["dcpm", "sleep"]},
    {"case_id": "SR-014", "query": "MetaForge forge stage recycle skill library",
     "expected_source": "lessons.jsonl", "expected_keywords": ["metaforge", "forge"]},
    {"case_id": "SR-015", "query": "Socratic-SWE SWE-bench 50.40 trace",
     "expected_source": "lessons.jsonl", "expected_keywords": ["socratic", "swe-bench"]},
    {"case_id": "SR-016", "query": "MLEvolve MLE-Bench 12 hour budget",
     "expected_source": "lessons.jsonl", "expected_keywords": ["mlevolve", "mle-bench"]},
    {"case_id": "SR-017", "query": "OpenSkill open world self evolution",
     "expected_source": "lessons.jsonl", "expected_keywords": ["openskill"]},
    {"case_id": "SR-018", "query": "Trust layer MCP A2A capability descriptor",
     "expected_source": "lessons.jsonl", "expected_keywords": ["trust", "layer", "mcp"]},
    {"case_id": "SR-019", "query": "装备厚度理论 L1 capability equivalence",
     "expected_source": "learned.md", "expected_keywords": ["装备厚度", "l1"]},
    {"case_id": "SR-020", "query": "consilium protocol BFT derived multi model",
     "expected_source": "lessons.jsonl", "expected_keywords": ["consilium", "bft"]},
]


def run_eval(limit: int | None = None) -> dict:
    chunks = load_index()
    if not chunks:
        return {"error": "No index. Run build-index first."}
    cases = EVAL_CASES[:limit] if limit else EVAL_CASES
    results_by_mode = {"keyword": [], "semantic": [], "hybrid": []}
    for case in cases:
        for mode in results_by_mode:
            top_results = recall(case["query"], chunks, mode=mode, top=5)
            hit = False
            for r in top_results:
                if r.source == case["expected_source"]:
                    kw_overlap = any(
                        kw.lower() in r.title.lower() or kw.lower() in r.snippet.lower()
                        for kw in case["expected_keywords"]
                    )
                    if kw_overlap:
                        hit = True
                        break
            results_by_mode[mode].append({
                "case_id": case["case_id"],
                "query": case["query"],
                "hit_top5": hit,
            })
    summary = {}
    for mode, results in results_by_mode.items():
        n = len(results)
        hits = sum(1 for r in results if r["hit_top5"])
        summary[mode] = {
            "total_cases": n,
            "top5_hits": hits,
            "top5_hit_rate": round(hits / n, 4) if n else 0,
        }
    return {"summary": summary, "details": results_by_mode}


def cmd_build_index(args: argparse.Namespace) -> int:
    print(f"Building semantic recall index...")
    chunks = build_index()
    save_index(chunks)
    print(f"OK: indexed {len(chunks)} chunks")
    by_source: dict[str, int] = {}
    for c in chunks:
        by_source[c.source] = by_source.get(c.source, 0) + 1
    for src, c in sorted(by_source.items()):
        print(f"  {src}: {c}")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    chunks = load_index()
    if not chunks:
        print("No index. Run build-index first.")
        return 1
    results = recall(args.query, chunks, mode=args.mode, top=args.top)
    print(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    result = run_eval(limit=args.limit)
    if "error" in result:
        print(result["error"])
        return 1
    print(json.dumps(result["summary"], indent=2))
    if args.save_details:
        EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EVAL_PATH, "w") as f:
            for mode, cases in result["details"].items():
                for c in cases:
                    f.write(json.dumps({"mode": mode, **c}) + "\n")
        print(f"\nDetails saved: {EVAL_PATH}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    chunks = load_index()
    if not chunks:
        print("No index. Run build-index first.")
        return 1
    by_source: dict[str, int] = {}
    total_tokens = 0
    for c in chunks:
        by_source[c.source] = by_source.get(c.source, 0) + 1
        total_tokens += c.doc_length
    print(f"Index stats:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Avg chunk length: {total_tokens // len(chunks) if chunks else 0}")
    for src, c in sorted(by_source.items()):
        print(f"  {src}: {c}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Semantic Memory Recall v1.0 (Phase 4)")
    sub = p.add_subparsers(dest="cmd", required=True)
    p_build = sub.add_parser("build-index", help="Build full index")
    p_build.set_defaults(func=cmd_build_index)
    p_q = sub.add_parser("query", help="Query the index")
    p_q.add_argument("query", help="Query text")
    p_q.add_argument("--mode", default="hybrid", choices=["keyword", "semantic", "hybrid"])
    p_q.add_argument("--top", type=int, default=5)
    p_q.set_defaults(func=cmd_query)
    p_eval = sub.add_parser("eval", help="Run eval suite")
    p_eval.add_argument("--limit", type=int, default=None)
    p_eval.add_argument("--save-details", action="store_true")
    p_eval.set_defaults(func=cmd_eval)
    p_stats = sub.add_parser("stats", help="Index statistics")
    p_stats.set_defaults(func=cmd_stats)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())