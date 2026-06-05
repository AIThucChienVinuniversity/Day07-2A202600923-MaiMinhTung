from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved = self.store.search(question, top_k=top_k)

        if not retrieved:
            return "No relevant information found."

        context = "\n\n".join(
            item["content"]
            for item in retrieved
        )

        prompt = f"""
    Use the following context to answer the question.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """.strip()

        return self.llm_fn(prompt)