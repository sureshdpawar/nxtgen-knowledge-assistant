class PromptBuilderService:

    def build(
        self,
        query: str,
        contexts: list[str],
    ) -> str:

        context = "\n\n".join(contexts)

        return f"""You are an AI assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:

"I couldn't find that information in the provided documents."

Context:
---------
{context}

Question:
---------
{query}

Answer:
"""