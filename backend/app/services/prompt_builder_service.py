class PromptBuilderService:

    def build(
        self,
        query: str,
        contexts: list[str],
        history: list | None = None,
    ) -> str:

        history = history or []

        conversation = ""

        if history:

            conversation = "\n".join(
                [
                    f"{message.role.title()}: {message.content}"
                    for message in history
                ]
            )

        context = "\n\n".join(contexts)

        prompt = f"""
You are an AI assistant.

Use ONLY the provided context to answer the user's question.

If the answer cannot be found in the context, say:

"I don't have enough information in the knowledge base."

-------------------------
Conversation History
-------------------------

{conversation}

-------------------------
Knowledge Base Context
-------------------------

{context}

-------------------------
Current Question
-------------------------

{query}

Provide a concise and accurate answer.
"""

        return prompt.strip()