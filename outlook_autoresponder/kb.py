from pathlib import Path
from .models import KnowledgeHit


def load_kb_documents(kb_path: Path):
    docs = []
    for path in sorted(kb_path.rglob('*')):
        if path.is_file() and path.suffix.lower() in {'.md', '.txt'}:
            docs.append({'path': str(path), 'text': path.read_text(errors='ignore')})
    return docs


def simple_search(query: str, docs, limit: int = 5):
    query_terms = [term.lower() for term in query.split() if term.strip()]
    scored = []
    for doc in docs:
        text = doc['text'].lower()
        score = sum(text.count(term) for term in query_terms)
        if score > 0:
            scored.append(KnowledgeHit(path=doc['path'], text=doc['text'], score=score))
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]
