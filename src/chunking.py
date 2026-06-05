from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []

        for start in range(0, len(text), step):
            chunk = text[start:start + self.chunk_size]
            chunks.append(chunk)

            if start + self.chunk_size >= len(text):
                break

        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sentences = re.split(r"(?<=[.!?])(?:\s+|\n+)", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks: list[str] = []

        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        return self._split(text.strip(), self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]

        if separator == "":
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        parts = current_text.split(separator)
        chunks: list[str] = []
        buffer = ""

        for part in parts:
            if not part:
                continue

            candidate = part if not buffer else buffer + separator + part

            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(
                        self._split(buffer.strip(), remaining_separators[1:])
                    )

                if len(part) > self.chunk_size:
                    chunks.extend(
                        self._split(part.strip(), remaining_separators[1:])
                    )
                    buffer = ""
                else:
                    buffer = part

        if buffer:
            chunks.extend(self._split(buffer.strip(), remaining_separators[1:]))

        return [chunk for chunk in chunks if chunk]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result = {}

        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            lengths = [len(chunk) for chunk in chunks]

            result[name] = {
                "count": len(chunks),
                "avg_length": sum(lengths) / len(lengths) if lengths else 0,
                "chunks": chunks,
            }

        return result


if __name__ == "__main__":
    sample_text = """
    Retrieval-Augmented Generation combines information retrieval with text generation.
    First, documents are split into smaller chunks. Then embeddings are created for each chunk.
    When a user asks a question, the system retrieves the most relevant chunks.
    Finally, the language model uses those chunks to answer more accurately.

    Chunking strategy is important. If chunks are too small, context may be lost.
    If chunks are too large, retrieval may become noisy.
    """

    comparator = ChunkingStrategyComparator()
    result = comparator.compare(sample_text, chunk_size=120)

    for strategy_name, info in result.items():
        print(f"\n=== {strategy_name.upper()} ===")
        print("num_chunks:", info["num_chunks"])
        print("avg_chunk_length:", info["avg_chunk_length"])
        print("min_chunk_length:", info["min_chunk_length"])
        print("max_chunk_length:", info["max_chunk_length"])

        for i, chunk in enumerate(info["chunks"], start=1):
            print(f"\nChunk {i}:")
            print(chunk)