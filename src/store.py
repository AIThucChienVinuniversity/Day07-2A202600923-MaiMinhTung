from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=self._collection_name
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)

        metadata = dict(doc.metadata or {})

        if "doc_id" not in metadata:
            metadata["doc_id"] = getattr(doc, "id", None) or getattr(doc, "doc_id", None)

        return {
            "id": str(self._next_index),
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
        }

    def _search_records(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)

        scored = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        if not docs:
            return

        records = []

        for doc in docs:
            record = self._make_record(doc)
            records.append(record)
            self._next_index += 1

        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=[record["id"] for record in records],
                documents=[record["content"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []

        if self._use_chroma and self._collection is not None:
            results = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
            )

            output = []
            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i in range(len(ids)):
                output.append({
                    "id": ids[i],
                    "content": docs[i],
                    "metadata": metadatas[i] or {},
                    "score": -distances[i] if distances else 0.0,
                })

            return output

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        if self._use_chroma and self._collection is not None:
            return self._collection.count()

        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict]:
        if metadata_filter is None:
            metadata_filter = {}

        if not metadata_filter:
            return self.search(query, top_k)

        if self._use_chroma and self._collection is not None:
            results = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
                where=metadata_filter,
            )

            output = []
            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i in range(len(ids)):
                output.append({
                    "id": ids[i],
                    "content": docs[i],
                    "metadata": metadatas[i] or {},
                    "score": -distances[i] if distances else 0.0,
                })

            return output

        filtered_records = [
            record for record in self._store
            if all(
                record["metadata"].get(key) == value
                for key, value in metadata_filter.items()
            )
        ]

        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        old_size = len(self._store)

        self._store = [
            record for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]

        return len(self._store) < old_size