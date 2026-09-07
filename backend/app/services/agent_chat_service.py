from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any
from uuid import (
    UUID,
    uuid4,
)

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import (
    AgentRunStatus,
    AgentStatus,
)
from app.models.agent_run import (
    AgentRun,
)
from app.models.conversation import (
    Conversation,
)
from app.models.user import User
from app.services.agent_execution_service import (
    AgentExecutionService,
)
from app.services.agent_service import (
    AgentService,
)
from app.services.conversation_service import (
    ConversationService,
)


ProgressCallback = Callable[
    [dict[str, Any]],
    Awaitable[None] | None,
]


class AgentChatService:

    def __init__(self):
        self.agent_service = (
            AgentService()
        )
        self.execution_service = (
            AgentExecutionService()
        )
        self.conversation_service = (
            ConversationService()
        )

    async def _emit_progress(
        self,
        progress_callback:
            ProgressCallback | None,
        event: dict[str, Any],
    ) -> None:
        if progress_callback is None:
            return

        result = progress_callback(
            event,
        )

        if (
            result is not None
            and hasattr(
                result,
                "__await__",
            )
        ):
            await result

    def _get_owned_conversation(
        self,
        *,
        db: Session,
        current_user: User,
        conversation_id: UUID,
    ) -> Conversation:
        conversation = (
            self.conversation_service
            .get_conversation(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                user_id=
                    current_user.id,
                conversation_id=
                    conversation_id,
            )
        )

        if conversation is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=
                    "Conversation not found.",
            )

        if (
            conversation.agent_id
            is None
            or conversation.agent_thread_id
            is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Conversation is not an "
                    "agent chat."
                ),
            )

        return conversation

    def _ensure_active_agent(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ):
        agent = self.agent_service.get(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        if (
            agent.status
            != AgentStatus.ACTIVE
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Agent must be active "
                    "before it can run."
                ),
            )

        return agent

    def _pending_approval_run(
        self,
        *,
        db: Session,
        current_user: User,
        conversation: Conversation,
    ) -> AgentRun | None:
        if (
            conversation.agent_id
            is None
            or conversation.agent_thread_id
            is None
        ):
            return None

        stmt = (
            select(
                AgentRun
            )
            .where(
                AgentRun.tenant_id
                == current_user.tenant_id,

                AgentRun.agent_id
                == conversation.agent_id,

                AgentRun.user_id
                == current_user.id,

                AgentRun.thread_id
                == conversation.agent_thread_id,

                AgentRun.status
                == (
                    AgentRunStatus
                    .WAITING_FOR_APPROVAL
                ),
            )
            .order_by(
                AgentRun.started_at.desc()
            )
        )

        return (
            db.scalars(
                stmt
            )
            .first()
        )

    def _create_conversation(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=
                current_user.tenant_id,
            user_id=
                current_user.id,
            chat_channel_id=None,
            knowledge_base_id=None,
            agent_id=agent_id,
            agent_thread_id=uuid4(),
            title=title,
        )

        db.add(
            conversation
        )

        db.commit()

        db.refresh(
            conversation
        )

        return conversation

    def _get_or_create_conversation(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        conversation_id:
            UUID | None,
        title: str,
    ) -> Conversation:
        if conversation_id is None:
            return (
                self._create_conversation(
                    db=db,
                    current_user=current_user,
                    agent_id=agent_id,
                    title=title,
                )
            )

        conversation = (
            self._get_owned_conversation(
                db=db,
                current_user=current_user,
                conversation_id=
                    conversation_id,
            )
        )

        if (
            conversation.agent_id
            != agent_id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Conversation belongs "
                    "to a different agent."
                ),
            )

        return conversation

    def _result(
        self,
        *,
        conversation: Conversation,
        run_result: dict,
    ) -> dict:
        return {
            "conversation_id":
                conversation.id,
            "agent_id":
                conversation.agent_id,
            "run_id":
                run_result[
                    "run_id"
                ],
            "thread_id":
                run_result[
                    "thread_id"
                ],
            "checkpoint_id":
                run_result[
                    "checkpoint_id"
                ],
            "answer":
                run_result[
                    "answer"
                ],
            "status":
                run_result[
                    "status"
                ],
            "llm_calls":
                run_result[
                    "llm_calls"
                ],
            "tools_used":
                run_result[
                    "tools_used"
                ],
            "duration_ms":
                run_result[
                    "duration_ms"
                ],
            "interrupts":
                run_result.get(
                    "interrupts",
                    [],
                ),
        }

    async def run(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        query: str,
        conversation_id:
            UUID | None = None,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        clean_query = (
            query.strip()
        )

        if not clean_query:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Agent query cannot "
                    "be empty."
                ),
            )

        self._ensure_active_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        conversation = (
            self._get_or_create_conversation(
                db=db,
                current_user=current_user,
                agent_id=agent_id,
                conversation_id=
                    conversation_id,
                title=
                    clean_query[:500],
            )
        )

        pending_run = (
            self._pending_approval_run(
                db=db,
                current_user=current_user,
                conversation=conversation,
            )
        )

        if pending_run is not None:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail={
                    "message": (
                        "This conversation has "
                        "a pending tool approval."
                    ),
                    "run_id":
                        str(
                            pending_run.id
                        ),
                },
            )

        await self._emit_progress(
            progress_callback,
            {
                "type":
                    "conversation",
                "conversation_id":
                    str(
                        conversation.id
                    ),
                "agent_id":
                    str(
                        agent_id
                    ),
                "thread_id":
                    str(
                        conversation
                        .agent_thread_id
                    ),
            },
        )

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=
                conversation.id,
            content=clean_query,
        )

        run_result = (
            await
            self.execution_service.run(
                db=db,
                current_user=current_user,
                agent_id=agent_id,
                query=clean_query,
                thread_id=
                    conversation
                    .agent_thread_id,
                progress_callback=
                    progress_callback,
            )
        )

        if (
            run_result[
                "status"
            ]
            == AgentRunStatus.COMPLETED
            and run_result.get(
                "answer"
            )
        ):
            self.conversation_service.save_assistant_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    run_result[
                        "answer"
                    ],
                citations=[],
                token_usage={},
            )

        return self._result(
            conversation=conversation,
            run_result=run_result,
        )

    async def resume(
        self,
        *,
        db: Session,
        current_user: User,
        conversation_id: UUID,
        run_id: UUID,
        decision: str,
        reason: str | None = None,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        conversation = (
            self._get_owned_conversation(
                db=db,
                current_user=current_user,
                conversation_id=
                    conversation_id,
            )
        )

        agent_id = (
            conversation.agent_id
        )

        if agent_id is None:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Conversation is not an "
                    "agent chat."
                ),
            )

        self._ensure_active_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        run = db.get(
            AgentRun,
            run_id,
        )

        if (
            run is None
            or run.tenant_id
            != current_user.tenant_id
            or run.agent_id
            != agent_id
            or run.user_id
            != current_user.id
            or run.thread_id
            != conversation.agent_thread_id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=
                    "Agent run not found.",
            )

        await self._emit_progress(
            progress_callback,
            {
                "type":
                    "conversation",
                "conversation_id":
                    str(
                        conversation.id
                    ),
                "agent_id":
                    str(
                        agent_id
                    ),
                "thread_id":
                    str(
                        conversation
                        .agent_thread_id
                    ),
                "run_id":
                    str(
                        run_id
                    ),
            },
        )

        run_result = (
            await
            self.execution_service.resume(
                db=db,
                current_user=current_user,
                agent_id=agent_id,
                run_id=run_id,
                decision=decision,
                reason=reason,
                progress_callback=
                    progress_callback,
            )
        )

        if (
            run_result[
                "status"
            ]
            == AgentRunStatus.COMPLETED
            and run_result.get(
                "answer"
            )
        ):
            self.conversation_service.save_assistant_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    run_result[
                        "answer"
                    ],
                citations=[],
                token_usage={},
            )

        return self._result(
            conversation=conversation,
            run_result=run_result,
        )
