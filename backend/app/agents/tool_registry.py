from uuid import UUID

from langchain_core.tools import (
    BaseTool,
)
from sqlalchemy.orm import Session

from app.agents.tools.knowledge_search import (
    create_knowledge_search_tool,
)


class AgentToolRegistry:

    def get_tools(
        self,
        db: Session,
        knowledge_base_ids:
            list[UUID],
    ) -> list[BaseTool]:

        tools: list[
            BaseTool
        ] = []

        if knowledge_base_ids:
            tools.append(
                create_knowledge_search_tool(
                    db=db,
                    knowledge_base_ids=
                        knowledge_base_ids,
                )
            )

        return tools