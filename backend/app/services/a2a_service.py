from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.a2a_context import a2a_delegation_depth
from app.core.enums import AgentRunStatus, AgentStatus
from app.models.agent import Agent
from app.models.user import User
from app.schemas.a2a import (
    A2AMessage,
    A2APart,
    A2ASendMessageRequest,
    A2ASendMessageResponse,
)
from app.services.agent_access_service import AgentAccessService
from app.services.guardrails_service import (
    GuardrailBlockedError,
    GuardrailsService,
)


class A2AService:
    """Small A2A v1 boundary for Knowgentiq.

    Scope: per-agent card discovery and synchronous text SendMessage.
    Same-process agents invoke the exact same A2A request/response
    contract in-process rather than making a loopback HTTP request.
    The HTTP+JSON binding is also exposed for external A2A clients.
    """

    def __init__(self):
        self.access_service = AgentAccessService()
        self.guardrails_service = GuardrailsService()

    def _target_by_tenant(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        agent_id: UUID,
    ) -> Agent:
        agent = db.get(Agent, agent_id)
        if (
            agent is None
            or agent.tenant_id != tenant_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A2A target agent not found.",
            )
        if agent.status != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A2A target agent is not active.",
            )
        return agent

    def agent_card_for_agent(
        self,
        *,
        agent: Agent,
        interface_url: str,
    ) -> dict:
        description = (
            str(agent.description or "").strip()
            or f"Knowgentiq agent: {agent.name}"
        )
        return {
            "name": agent.name,
            "description": description,
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "extendedAgentCard": False,
            },
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["text/plain"],
            "supportedInterfaces": [
                {
                    "url": interface_url,
                    "protocolBinding": "HTTP+JSON",
                    "protocolVersion": "1.0",
                }
            ],
            "skills": [
                {
                    "id": f"knowgentiq-agent-{agent.id}",
                    "name": agent.name,
                    "description": description,
                    "tags": [
                        "knowgentiq",
                        "enterprise-agent",
                        "a2a",
                    ],
                    "examples": [],
                    "inputModes": ["text/plain"],
                    "outputModes": ["text/plain"],
                }
            ],
        }

    def authenticated_agent_card(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        interface_url: str,
    ) -> dict:
        agent = self.access_service.require_agent_access(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )
        if agent.status != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Agent must be active before A2A discovery.",
            )
        return self.agent_card_for_agent(
            agent=agent,
            interface_url=interface_url,
        )

    def _text_from_message(
        self,
        payload: A2ASendMessageRequest,
    ) -> str:
        if payload.message.role != "ROLE_USER":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SendMessage currently accepts ROLE_USER only.",
            )
        parts = [
            str(part.text).strip()
            for part in payload.message.parts
            if part.text is not None
            and str(part.text).strip()
        ]
        if not parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This A2A slice supports text parts only.",
            )
        return "\n".join(parts)

    async def _execute_send_message(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        target: Agent,
        payload: A2ASendMessageRequest,
        actor_type: str,
        actor_id: str,
        runtime_context: dict | None = None,
        context_metadata: dict | None = None,
    ) -> A2ASendMessageResponse:
        query = self._text_from_message(payload)

        try:
            guarded_query = await self.guardrails_service.check_input_async(
                query
            )
        except GuardrailBlockedError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        # Lazy import avoids an import cycle with AgentToolRegistry.
        from app.services.agent_execution_service import AgentExecutionService

        result = await AgentExecutionService().run_external(
            db=db,
            tenant_id=tenant_id,
            agent_id=target.id,
            query=guarded_query,
            actor_type=actor_type,
            actor_id=actor_id,
            runtime_context=runtime_context,
            context_metadata=context_metadata,
            # The first demo is intended for informational/RAG child agents.
            # Approval-requiring actions are never promoted to AUTO here.
            auto_execute_tool_names=set(),
        )

        if result["status"] != AgentRunStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "A2A target did not complete synchronously.",
                    "status": result["status"].value,
                    "run_id": str(result["run_id"]),
                },
            )

        answer = str(result.get("answer") or "")
        try:
            answer = await self.guardrails_service.check_output_async(answer)
        except GuardrailBlockedError as exc:
            answer = str(exc)

        return A2ASendMessageResponse(
            message=A2AMessage(
                messageId=str(uuid4()),
                contextId=(
                    payload.message.context_id
                    or str(result["thread_id"])
                ),
                role="ROLE_AGENT",
                parts=[
                    A2APart(
                        text=answer,
                        mediaType="text/plain",
                    )
                ],
                metadata={
                    "knowgentiq": {
                        "agentId": str(target.id),
                        "runId": str(result["run_id"]),
                        "toolsUsed": result.get("tools_used", []),
                        "durationMs": result.get("duration_ms"),
                    }
                },
            )
        )

    async def delegate(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        source_agent_id: UUID,
        target_agent_id: UUID,
        message: str,
    ) -> dict:
        depth = a2a_delegation_depth.get()
        if depth >= 1:
            raise RuntimeError(
                "This A2A demo supports one delegation hop only."
            )

        source = self._target_by_tenant(
            db=db,
            tenant_id=tenant_id,
            agent_id=source_agent_id,
        )
        target = self._target_by_tenant(
            db=db,
            tenant_id=tenant_id,
            agent_id=target_agent_id,
        )

        # Discovery is explicit even for same-process delegation. The
        # configured connection resolves a target whose Agent Card declares
        # the A2A interface and skill/capability description.
        card = self.agent_card_for_agent(
            agent=target,
            interface_url=(
                f"/api/v1/a2a/agents/{target.id}"
            ),
        )

        clean_message = message.strip()
        if not clean_message:
            raise ValueError("A2A delegation message cannot be empty.")

        a2a_request = A2ASendMessageRequest(
            message=A2AMessage(
                messageId=str(uuid4()),
                role="ROLE_USER",
                parts=[
                    A2APart(
                        text=clean_message,
                        mediaType="text/plain",
                    )
                ],
                metadata={
                    "knowgentiq": {
                        "callingAgentId": str(source.id),
                        "callingAgentName": source.name,
                    }
                },
            )
        )

        token = a2a_delegation_depth.set(depth + 1)
        try:
            response = await self._execute_send_message(
                db=db,
                tenant_id=tenant_id,
                target=target,
                payload=a2a_request,
                actor_type="A2A_AGENT",
                actor_id=str(source_agent_id),
                runtime_context={
                    "calling_agent_id": str(source_agent_id),
                    "calling_agent_name": source.name,
                    "protocol": "A2A",
                    "protocol_version": "1.0",
                },
                context_metadata={
                    "protocol": "A2A",
                    "protocol_version": "1.0",
                    "calling_agent_id": str(source_agent_id),
                    "calling_agent_name": source.name,
                    "target_agent_id": str(target_agent_id),
                    "target_agent_name": target.name,
                },
            )
        finally:
            a2a_delegation_depth.reset(token)

        metadata = (
            response.message.metadata
            or {}
        ).get("knowgentiq", {})

        answer = "\n".join(
            str(part.text)
            for part in response.message.parts
            if part.text
        )

        return {
            "protocol": "A2A",
            "protocol_version": "1.0",
            "operation": "SendMessage",
            "discovered_agent": card["name"],
            "target_agent_id": str(target.id),
            "child_run_id": metadata.get("runId"),
            "status": "COMPLETED",
            "tools_used": metadata.get("toolsUsed", []),
            "duration_ms": metadata.get("durationMs"),
            "answer": answer,
        }

    async def send_message_authenticated(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        payload: A2ASendMessageRequest,
    ) -> dict:
        target = self.access_service.require_agent_access(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )
        if target.status != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A2A target agent is not active.",
            )

        response = await self._execute_send_message(
            db=db,
            tenant_id=current_user.tenant_id,
            target=target,
            payload=payload,
            actor_type="A2A_CLIENT",
            actor_id=str(current_user.id),
            context_metadata={
                "protocol": "A2A",
                "protocol_version": "1.0",
            },
        )

        return response.model_dump(
            by_alias=True,
            exclude_none=True,
        )
