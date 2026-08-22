import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
)
from app.services.chat_channel_slack_service import (
    ChatChannelSlackService,
)
from app.services.slack_request_verification_service import (
    SlackRequestVerificationService,
)


logger = logging.getLogger(
    "nxtgen.slack"
)


router = APIRouter(
    prefix="/slack",
    tags=[
        "Public Slack"
    ],
)


slack_service = (
    ChatChannelSlackService()
)

verification_service = (
    SlackRequestVerificationService()
)


@router.post(
    "/events",
)
async def slack_events(
    request: Request,

    db: Session = Depends(
        get_db
    ),
):
    raw_body = await request.body()

    try:
        payload = json.loads(
            raw_body
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Invalid Slack payload."
            ),
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Invalid Slack payload."
            ),
        )

    slack_team_id = (
        payload.get(
            "team_id"
        )
    )

    if not slack_team_id:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Slack team ID is missing."
            ),
        )

    credential = (
        slack_service
        .get_credential_by_team_id(
            db=db,
            slack_team_id=(
                slack_team_id
            ),
        )
    )

    if credential is None:
        logger.warning(
            "Slack request received "
            "for unknown workspace "
            "team_id=%s",
            slack_team_id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Unknown Slack workspace."
            ),
        )

    timestamp = (
        request.headers.get(
            "X-Slack-Request-Timestamp"
        )
    )

    signature = (
        request.headers.get(
            "X-Slack-Signature"
        )
    )

    valid_signature = (
        verification_service.verify(
            signing_secret=(
                credential
                .signing_secret
            ),
            timestamp=(
                timestamp
            ),
            signature=(
                signature
            ),
            raw_body=(
                raw_body
            ),
        )
    )

    if not valid_signature:
        logger.warning(
            "Invalid Slack request "
            "signature "
            "team_id=%s",
            slack_team_id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid Slack signature."
            ),
        )

    payload_type = (
        payload.get(
            "type"
        )
    )

    #
    # Slack verifies the configured
    # Events API URL by sending a
    # url_verification request.
    #
    if (
        payload_type
        == "url_verification"
    ):
        challenge = (
            payload.get(
                "challenge"
            )
        )

        if not challenge:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Slack verification "
                    "challenge is missing."
                ),
            )

        logger.info(
            "Slack Events API URL "
            "verified "
            "team_id=%s",
            slack_team_id,
        )

        return {
            "challenge":
                challenge,
        }

    #
    # We are deliberately not processing
    # normal Slack events yet.
    #
    # Slack must receive a successful
    # acknowledgement while we build
    # the next event-processing step.
    #
    if (
        payload_type
        == "event_callback"
    ):
        event = (
            payload.get(
                "event"
            )
            or {}
        )

        logger.info(
            "Slack event received "
            "team_id=%s "
            "event_id=%s "
            "event_type=%s",
            slack_team_id,
            payload.get(
                "event_id"
            ),
            event.get(
                "type"
            ),
        )

        return {
            "ok":
                True,
        }

    logger.info(
        "Ignoring unsupported Slack "
        "payload "
        "team_id=%s "
        "payload_type=%s",
        slack_team_id,
        payload_type,
    )

    return {
        "ok":
            True,
    }