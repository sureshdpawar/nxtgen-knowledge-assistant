from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
)
from app.auth.dependencies import (
    get_current_active_user,
)
from app.models.user import (
    User,
)
from app.schemas.chat_channel import (
    ChatChannelApiKeyCreate,
    ChatChannelApiKeyCreatedResponse,
    ChatChannelApiKeyResponse,
    ChatChannelCreate,
    ChatChannelResponse,
    ChatChannelUpdate,
)
from app.schemas.chat_channel_metrics import (
    ChatChannelMetricsResponse,
)
from app.schemas.conversation import (
    ChannelConversationListResponse,
    ChannelConversationResponse,
)
from app.services.chat_channel_metrics_service import (
    ChatChannelMetricsService,
)
from app.services.chat_channel_service import (
    ChatChannelService,
)
from app.services.conversation_service import (
    ConversationService,
)


router = APIRouter(
    prefix="/channels",
    tags=[
        "Chat Channels"
    ],
)


service = (
    ChatChannelService()
)

conversation_service = (
    ConversationService()
)

metrics_service = (
    ChatChannelMetricsService()
)


# ---------------------------------------------------------
# Channels
# ---------------------------------------------------------


@router.post(
    "",
    response_model=(
        ChatChannelResponse
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def create_channel(
    payload:
        ChatChannelCreate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        return (
            service.create_channel(
                db=db,
                current_user=(
                    current_user
                ),
                knowledge_base_id=(
                    payload
                    .knowledge_base_id
                ),
                name=(
                    payload.name
                ),
                channel_type=(
                    payload.type
                ),
                configuration=(
                    payload.configuration
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.get(
    "",
    response_model=list[
        ChatChannelResponse
    ],
)
def list_channels(
    knowledge_base_id:
        UUID | None = Query(
            default=None
        ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    return (
        service.list_channels(
            db=db,
            current_user=(
                current_user
            ),
            knowledge_base_id=(
                knowledge_base_id
            ),
        )
    )


@router.get(
    "/{channel_id}/metrics",
    response_model=(
        ChatChannelMetricsResponse
    ),
)
def get_channel_metrics(
    channel_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        channel = (
            service.get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

        metrics = (
            metrics_service
            .get_metrics(
                db=db,
                tenant_id=(
                    current_user
                    .tenant_id
                ),
                chat_channel_id=(
                    channel.id
                ),
            )
        )

        api_keys = []

        if (
            channel.type.value
            == "PUBLIC_API"
        ):
            api_keys = (
                service.list_api_keys(
                    db=db,
                    current_user=(
                        current_user
                    ),
                    channel_id=(
                        channel.id
                    ),
                )
            )

        active_api_key_count = sum(
            1
            for api_key
            in api_keys
            if api_key.active
        )

        revoked_api_key_count = sum(
            1
            for api_key
            in api_keys
            if not api_key.active
        )

        return (
            ChatChannelMetricsResponse(
                conversation_count=(
                    metrics[
                        "conversation_count"
                    ]
                ),
                message_count=(
                    metrics[
                        "message_count"
                    ]
                ),
                user_message_count=(
                    metrics[
                        "user_message_count"
                    ]
                ),
                assistant_message_count=(
                    metrics[
                        "assistant_message_count"
                    ]
                ),
                last_activity_at=(
                    metrics[
                        "last_activity_at"
                    ]
                ),
                active_api_key_count=(
                    active_api_key_count
                ),
                revoked_api_key_count=(
                    revoked_api_key_count
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.get(
    "/{channel_id}",
    response_model=(
        ChatChannelResponse
    ),
)
def get_channel(
    channel_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        return (
            service.get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.patch(
    "/{channel_id}",
    response_model=(
        ChatChannelResponse
    ),
)
def update_channel(
    channel_id: UUID,

    payload:
        ChatChannelUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        return (
            service.update_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
                name=(
                    payload.name
                ),
                status=(
                    payload.status
                ),
                configuration=(
                    payload.configuration
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.delete(
    "/{channel_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_channel(
    channel_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        service.delete_channel(
            db=db,
            current_user=(
                current_user
            ),
            channel_id=(
                channel_id
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )


# ---------------------------------------------------------
# API keys
# ---------------------------------------------------------


@router.post(
    "/{channel_id}/api-keys",
    response_model=(
        ChatChannelApiKeyCreatedResponse
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def create_api_key(
    channel_id: UUID,

    payload:
        ChatChannelApiKeyCreate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        (
            key_record,
            raw_api_key,
        ) = (
            service.create_api_key(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
                name=(
                    payload.name
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                exc
            ),
        ) from exc

    return (
        ChatChannelApiKeyCreatedResponse(
            id=(
                key_record.id
            ),
            name=(
                key_record.name
            ),
            key_prefix=(
                key_record
                .key_prefix
            ),
            api_key=(
                raw_api_key
            ),
        )
    )


@router.get(
    "/{channel_id}/api-keys",
    response_model=list[
        ChatChannelApiKeyResponse
    ],
)
def list_api_keys(
    channel_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        return (
            service.list_api_keys(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.delete(
    "/{channel_id}/api-keys/{key_id}",
    response_model=(
        ChatChannelApiKeyResponse
    ),
)
def revoke_api_key(
    channel_id: UUID,
    key_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        return (
            service.revoke_api_key(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
                key_id=(
                    key_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc


# ---------------------------------------------------------
# Channel conversations
# ---------------------------------------------------------


@router.get(
    "/{channel_id}/conversations",
    response_model=(
        ChannelConversationListResponse
    ),
)
def list_channel_conversations(
    channel_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        channel = (
            service.get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc

    conversations = (
        conversation_service
        .list_channel_conversations(
            db=db,
            tenant_id=(
                current_user
                .tenant_id
            ),
            chat_channel_id=(
                channel.id
            ),
        )
    )

    return (
        ChannelConversationListResponse(
            conversations=(
                conversations
            ),
        )
    )


@router.get(
    "/{channel_id}/conversations/{conversation_id}",
    response_model=(
        ChannelConversationResponse
    ),
)
def get_channel_conversation(
    channel_id: UUID,
    conversation_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        channel = (
            service.get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc

    conversation = (
        conversation_service
        .get_channel_conversation_with_messages(
            db=db,
            tenant_id=(
                current_user
                .tenant_id
            ),
            chat_channel_id=(
                channel.id
            ),
            conversation_id=(
                conversation_id
            ),
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Channel conversation "
                "not found."
            ),
        )

    return conversation


@router.delete(
    "/{channel_id}/conversations/{conversation_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_channel_conversation(
    channel_id: UUID,
    conversation_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    try:
        channel = (
            service.get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(
                exc
            ),
        ) from exc

    deleted = (
        conversation_service
        .delete_channel_conversation(
            db=db,
            tenant_id=(
                current_user
                .tenant_id
            ),
            chat_channel_id=(
                channel.id
            ),
            conversation_id=(
                conversation_id
            ),
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Channel conversation "
                "not found."
            ),
        )

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )