"""
TF-IDF document retrieval over local markdown files.

Uses scikit-learn's TfidfVectorizer — no vector DB needed.
This keeps the demo self-contained and the retrieval logic transparent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Document:
    """A knowledge base document with metadata and content."""

    id: str
    title: str
    tags: list[str]
    content: str  # raw markdown body (no frontmatter)

    @property
    def token_estimate(self) -> int:
        """Rough token count (words × 1.3) — good enough for teaching."""
        return int(len(self.content.split()) * 1.3)


@dataclass
class SearchResult:
    """A ranked search hit with relevance score."""

    document: Document
    score: float  # cosine similarity, 0–1
    snippet: str  # first ~200 chars of content


# ── Frontmatter parser ──────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---\s*\n", re.DOTALL)


def _parse_markdown(path: Path) -> Document:
    """Parse a markdown file with YAML frontmatter into a Document."""
    raw = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {path}")
    meta = yaml.safe_load(match.group(1))
    body = raw[match.end() :].strip()
    return Document(
        id=meta["id"],
        title=meta["title"],
        tags=meta.get("tags", []),
        content=body,
    )


# ── Knowledge Base with TF-IDF index ────────────────────────────────


class KnowledgeBase:
    """
    Loads markdown docs from a directory and builds a TF-IDF index.

    This is the "selecting context" engine — it decides which documents
    are relevant enough to enter the LLM's context window.
    """

    def __init__(self, docs_dir: str | Path | None = None):
        if docs_dir is None:
            docs_dir = Path(__file__).parent / "knowledge_base"
        self.docs_dir = Path(docs_dir)
        self.documents: dict[str, Document] = {}
        self._vectorizer: TfidfVectorizer | None = None
        self._tfidf_matrix = None
        self._doc_ids: list[str] = []  # row-index → doc_id mapping
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Load all .md files and build the TF-IDF index."""
        for path in sorted(self.docs_dir.glob("*.md")):
            doc = _parse_markdown(path)
            self.documents[doc.id] = doc

        if not self.documents:
            raise FileNotFoundError(f"No .md files found in {self.docs_dir}")

        # Build index: combine title + tags + content for richer matching
        self._doc_ids = list(self.documents.keys())
        corpus = []
        for doc_id in self._doc_ids:
            doc = self.documents[doc_id]
            text = f"{doc.title} {' '.join(doc.tags)} {doc.content}"
            corpus.append(text)

        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),  # unigrams + bigrams for better matching
        )
        self._tfidf_matrix = self._vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """
        Search documents by TF-IDF cosine similarity.

        Returns up to top_k results sorted by relevance score.
        """
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        # Rank by score, filter out zero-relevance
        ranked = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )
        results = []
        for idx, score in ranked[:top_k]:
            if score < 0.01:
                continue
            doc = self.documents[self._doc_ids[idx]]
            snippet = doc.content[:200].replace("\n", " ").strip()
            if len(doc.content) > 200:
                snippet += "..."
            results.append(SearchResult(document=doc, score=float(score), snippet=snippet))
        return results

    def get_document(self, doc_id: str) -> Document | None:
        """Fetch a specific document by ID."""
        return self.documents.get(doc_id)

    def list_documents(self) -> list[dict]:
        """List all documents with their metadata (no full content)."""
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "tags": doc.tags,
                "token_estimate": doc.token_estimate,
            }
            for doc in self.documents.values()
        ]
