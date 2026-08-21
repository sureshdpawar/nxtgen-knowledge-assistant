import hashlib
import secrets

from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)
from app.models.chat_channel import (
    ChatChannel,
)
from app.models.chat_channel_api_key import (
    ChatChannelApiKey,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user import User
from app.repositories.chat_channel_api_key_repository import (
    ChatChannelApiKeyRepository,
)
from app.repositories.chat_channel_repository import (
    ChatChannelRepository,
)
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
)


class ChatChannelService:

    API_KEY_PREFIX = "nxtgen_pk_"

    def __init__(self):
        self.channel_repository = (
            ChatChannelRepository()
        )

        self.api_key_repository = (
            ChatChannelApiKeyRepository()
        )

        self.access_service = (
            KnowledgeBaseAccessService()
        )

    def create_channel(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
        name: str,
        channel_type: ChatChannelType,
        configuration: dict,
    ) -> ChatChannel:

        self.access_service.require_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=(
                knowledge_base_id
            ),
        )

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge base not found."
            )

        if (
            knowledge_base.tenant_id
            != current_user.tenant_id
        ):
            raise ValueError(
                "Knowledge base does not "
                "belong to this tenant."
            )

        channel = ChatChannel(
            tenant_id=(
                current_user.tenant_id
            ),
            knowledge_base_id=(
                knowledge_base_id
            ),
            name=name.strip(),
            type=channel_type,
            status=(
                ChatChannelStatus.ACTIVE
            ),
            configuration=(
                configuration
                or {}
            ),
        )

        self.channel_repository.create(
            db,
            channel,
        )

        db.commit()
        db.refresh(
            channel
        )

        return channel

    def get_channel(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
    ) -> ChatChannel:

        channel = (
            self.channel_repository
            .get_for_tenant(
                db=db,
                channel_id=channel_id,
                tenant_id=(
                    current_user.tenant_id
                ),
            )
        )

        if channel is None:
            raise ValueError(
                "Chat channel not found."
            )

        self.access_service.require_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=(
                channel.knowledge_base_id
            ),
        )

        return channel

    def list_channels(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id:
            UUID | None = None,
    ) -> list[ChatChannel]:

        if (
            knowledge_base_id
            is not None
        ):
            self.access_service.require_access(
                db=db,
                current_user=current_user,
                knowledge_base_id=(
                    knowledge_base_id
                ),
            )

            channels = (
                self.channel_repository
                .list_by_knowledge_base(
                    db=db,
                    knowledge_base_id=(
                        knowledge_base_id
                    ),
                )
            )

            return [
                channel
                for channel
                in channels
                if (
                    channel.tenant_id
                    == current_user.tenant_id
                )
            ]

        return (
            self.channel_repository
            .list_by_tenant(
                db=db,
                tenant_id=(
                    current_user.tenant_id
                ),
            )
        )

    def update_channel(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
        name: str | None = None,
        status:
            ChatChannelStatus
            | None = None,
        configuration:
            dict | None = None,
    ) -> ChatChannel:

        channel = self.get_channel(
            db=db,
            current_user=current_user,
            channel_id=channel_id,
        )

        if name is not None:
            channel.name = (
                name.strip()
            )

        if status is not None:
            channel.status = status

        if configuration is not None:
            channel.configuration = (
                configuration
            )

        self.channel_repository.update(
            db,
            channel,
        )

        db.commit()
        db.refresh(
            channel
        )

        return channel

    def delete_channel(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
    ) -> None:

        channel = self.get_channel(
            db=db,
            current_user=current_user,
            channel_id=channel_id,
        )

        self.channel_repository.delete(
            db,
            channel,
        )

        db.commit()

    def create_api_key(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
        name: str,
    ) -> tuple[
        ChatChannelApiKey,
        str,
    ]:

        channel = self.get_channel(
            db=db,
            current_user=current_user,
            channel_id=channel_id,
        )

        if (
            channel.type
            != ChatChannelType.PUBLIC_API
        ):
            raise ValueError(
                "API keys can only be "
                "created for PUBLIC_API "
                "channels."
            )

        raw_secret = (
            secrets.token_urlsafe(
                32
            )
        )

        api_key = (
            f"{self.API_KEY_PREFIX}"
            f"{raw_secret}"
        )

        key_hash = (
            self._hash_api_key(
                api_key
            )
        )

        key_prefix = (
            api_key[:20]
        )

        key_record = (
            ChatChannelApiKey(
                channel_id=(
                    channel.id
                ),
                name=(
                    name.strip()
                ),
                key_prefix=(
                    key_prefix
                ),
                key_hash=(
                    key_hash
                ),
                active=True,
            )
        )

        self.api_key_repository.create(
            db,
            key_record,
        )

        db.commit()
        db.refresh(
            key_record
        )

        return (
            key_record,
            api_key,
        )

    def list_api_keys(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
    ) -> list[
        ChatChannelApiKey
    ]:

        channel = self.get_channel(
            db=db,
            current_user=current_user,
            channel_id=channel_id,
        )

        return (
            self.api_key_repository
            .list_by_channel(
                db=db,
                channel_id=(
                    channel.id
                ),
            )
        )

    def revoke_api_key(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
        key_id: UUID,
    ) -> ChatChannelApiKey:

        channel = self.get_channel(
            db=db,
            current_user=current_user,
            channel_id=channel_id,
        )

        key_record = (
            self.api_key_repository
            .get_for_channel(
                db=db,
                key_id=key_id,
                channel_id=(
                    channel.id
                ),
            )
        )

        if key_record is None:
            raise ValueError(
                "API key not found."
            )

        key_record.active = False

        self.api_key_repository.update(
            db,
            key_record,
        )

        db.commit()
        db.refresh(
            key_record
        )

        return key_record

    def authenticate_api_key(
        self,
        db: Session,
        api_key: str,
    ) -> ChatChannel:

        if not api_key.startswith(
            self.API_KEY_PREFIX
        ):
            raise ValueError(
                "Invalid API key."
            )

        key_hash = (
            self._hash_api_key(
                api_key
            )
        )

        key_record = (
            self.api_key_repository
            .get_by_hash(
                db=db,
                key_hash=key_hash,
            )
        )

        if (
            key_record is None
            or not key_record.active
        ):
            raise ValueError(
                "Invalid or inactive "
                "API key."
            )

        channel = db.get(
            ChatChannel,
            key_record.channel_id,
        )

        if channel is None:
            raise ValueError(
                "Chat channel not found."
            )

        if (
            channel.status
            != ChatChannelStatus.ACTIVE
        ):
            raise ValueError(
                "Chat channel is inactive."
            )

        if (
            channel.type
            != ChatChannelType.PUBLIC_API
        ):
            raise ValueError(
                "API key is not associated "
                "with a public API channel."
            )

        key_record.last_used_at = (
            datetime.now(
                timezone.utc
            )
        )

        self.api_key_repository.update(
            db,
            key_record,
        )

        db.commit()

        return channel

    def _hash_api_key(
        self,
        api_key: str,
    ) -> str:

        return (
            hashlib.sha256(
                api_key.encode(
                    "utf-8"
                )
            )
            .hexdigest()
        )