from __future__ import annotations

from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.integration import (
    Integration,
)
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
)


class IntegrationService:

    def list(
        self,
        db: Session,
        current_user: User,
    ) -> list[Integration]:

        stmt = (
            select(
                Integration,
            )
            .where(
                Integration.tenant_id
                == current_user.tenant_id,
            )
            .order_by(
                Integration.name,
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    def get(
        self,
        db: Session,
        current_user: User,
        integration_id: UUID,
    ) -> Integration:

        stmt = (
            select(
                Integration,
            )
            .where(
                Integration.id
                == integration_id,
                Integration.tenant_id
                == current_user.tenant_id,
            )
        )

        integration = (
            db.scalars(
                stmt,
            )
            .first()
        )

        if integration is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=
                    "Integration not found.",
            )

        return integration

    def create(
        self,
        db: Session,
        current_user: User,
        payload: IntegrationCreate,
    ) -> Integration:

        integration = Integration(
            tenant_id=
                current_user.tenant_id,

            name=
                payload.name.strip(),

            integration_type=
                payload.integration_type,

            base_url=
                payload.base_url.strip(),

            auth_type=
                payload.auth_type,

            auth_config=
                payload.auth_config,

            configuration=
                payload.configuration,

            is_active=
                payload.is_active,
        )

        db.add(
            integration,
        )

        db.commit()

        db.refresh(
            integration,
        )

        return integration

    def update(
        self,
        db: Session,
        current_user: User,
        integration_id: UUID,
        payload: IntegrationUpdate,
    ) -> Integration:

        integration = self.get(
            db=db,
            current_user=
                current_user,
            integration_id=
                integration_id,
        )

        fields = (
            payload.model_fields_set
        )

        if "name" in fields:
            if (
                payload.name is None
                or not payload.name.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Integration name "
                        "is required."
                    ),
                )

            integration.name = (
                payload.name.strip()
            )

        if "base_url" in fields:
            if (
                payload.base_url is None
                or not payload.base_url.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Base URL is required."
                    ),
                )

            integration.base_url = (
                payload.base_url.strip()
            )

        if "auth_type" in fields:
            if (
                payload.auth_type
                is not None
            ):
                integration.auth_type = (
                    payload.auth_type
                )

        if "auth_config" in fields:
            integration.auth_config = (
                payload.auth_config
            )

        if "configuration" in fields:
            integration.configuration = (
                payload.configuration
            )

        if (
            "is_active" in fields
            and payload.is_active
            is not None
        ):
            integration.is_active = (
                payload.is_active
            )

        db.commit()

        db.refresh(
            integration,
        )

        return integration

    def delete(
        self,
        db: Session,
        current_user: User,
        integration_id: UUID,
    ) -> None:

        integration = self.get(
            db=db,
            current_user=
                current_user,
            integration_id=
                integration_id,
        )

        db.delete(
            integration,
        )

        db.commit()