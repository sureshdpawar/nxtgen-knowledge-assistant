from uuid import UUID

from app.agents.tool_registry import (
    AgentToolRegistry,
)
from app.db.session import (
    SessionLocal,
)


KNOWLEDGE_BASE_ID = UUID(
    "f21ab0f9-6f6f-43f1-8cf6-ecc364ca4d12"
)


def main():

    db = SessionLocal()

    try:
        registry = (
            AgentToolRegistry()
        )

        tools = (
            registry.get_tools(
                db=db,
                knowledge_base_ids=[
                    KNOWLEDGE_BASE_ID,
                ],
            )
        )

        print(
            "Tools:",
            [
                tool.name
                for tool in tools
            ],
        )

        knowledge_tool = (
            tools[0]
        )

        result = (
            knowledge_tool.invoke(
                {
                    "query":
                        (
                            "What information "
                            "does this knowledge "
                            "base contain?"
                        ),
                }
            )
        )

        print(
            result,
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()