import json
import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
)
from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)
from app.db.session import (
    SessionLocal,
)
from app.models.chat_channel import (
    ChatChannel,
)
from app.repositories.chat_channel_slack_credential_repository import (
    ChatChannelSlackCredentialRepository,
)
from app.services.slack_event_service import (
    SlackEventService,
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


credential_repository = (
    ChatChannelSlackCredentialRepository()
)

verification_service = (
    SlackRequestVerificationService()
)

event_service = (
    SlackEventService()
)


# ---------------------------------------------------------
# Background workers
# ---------------------------------------------------------


def process_slack_event_background(
    slack_team_id: str,
    event: dict,
) -> None:
    """
    Process Slack app_mention events
    after Slack has already received
    the HTTP acknowledgement.
    """

    db = SessionLocal()

    try:
        event_service.process_app_mention(
            db=db,
            slack_team_id=(
                slack_team_id
            ),
            event=(
                event
            ),
        )

    except Exception:
        logger.exception(
            "Unhandled Slack "
            "app_mention background "
            "task error "
            "team_id=%s",
            slack_team_id,
        )

        db.rollback()

    finally:
        db.close()


def process_slack_dm_background(
    slack_team_id: str,
    event: dict,
) -> None:
    """
    Process Slack direct messages
    after Slack has already received
    the HTTP acknowledgement.
    """

    db = SessionLocal()

    try:
        event_service.process_direct_message(
            db=db,
            slack_team_id=(
                slack_team_id
            ),
            event=(
                event
            ),
        )

    except Exception:
        logger.exception(
            "Unhandled Slack "
            "direct-message background "
            "task error "
            "team_id=%s",
            slack_team_id,
        )

        db.rollback()

    finally:
        db.close()


# ---------------------------------------------------------
# Slack Events API
# ---------------------------------------------------------


@router.post(
    "/events/{channel_id}",
)
async def slack_events(
    channel_id: UUID,

    request: Request,

    background_tasks:
        BackgroundTasks,

    db: Session = Depends(
        get_db
    ),
):
    # -----------------------------------------------------
    # Resolve NXTGEN Slack channel
    # -----------------------------------------------------

    channel = db.get(
        ChatChannel,
        channel_id,
    )


    if channel is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Slack channel not found."
            ),
        )


    if (
        channel.type
        != ChatChannelType.SLACK
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Channel is not a Slack "
                "channel."
            ),
        )


    if (
        channel.status
        != ChatChannelStatus.ACTIVE
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Slack channel is inactive."
            ),
        )


    # -----------------------------------------------------
    # Resolve Slack credentials
    # -----------------------------------------------------

    credential = (
        credential_repository
        .get_by_channel(
            db=db,
            channel_id=(
                channel.id
            ),
        )
    )


    if credential is None:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Slack workspace is not "
                "configured."
            ),
        )


    # -----------------------------------------------------
    # Read raw request body
    # -----------------------------------------------------

    raw_body = (
        await request.body()
    )


    # -----------------------------------------------------
    # Verify Slack signature BEFORE trusting payload
    # -----------------------------------------------------

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
            "channel_id=%s",
            channel.id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid Slack signature."
            ),
        )


    # -----------------------------------------------------
    # Parse payload after signature verification
    # -----------------------------------------------------

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


    payload_type = (
        payload.get(
            "type"
        )
    )


    # -----------------------------------------------------
    # Slack URL verification
    # -----------------------------------------------------

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
            "channel_id=%s",
            channel.id,
        )


        return {
            "challenge":
                challenge,
        }


    # -----------------------------------------------------
    # Ignore non-event callbacks
    # -----------------------------------------------------

    if (
        payload_type
        != "event_callback"
    ):
        logger.info(
            "Ignoring Slack payload "
            "channel_id=%s "
            "payload_type=%s",
            channel.id,
            payload_type,
        )

        return {
            "ok":
                True,
        }


    # -----------------------------------------------------
    # Validate Slack workspace
    # -----------------------------------------------------

    slack_team_id = (
        payload.get(
            "team_id"
        )
    )


    if not slack_team_id:
        logger.warning(
            "Slack event missing "
            "team_id "
            "channel_id=%s",
            channel.id,
        )

        return {
            "ok":
                True,
        }


    if (
        slack_team_id
        != credential.slack_team_id
    ):
        logger.warning(
            "Slack workspace mismatch "
            "channel_id=%s "
            "expected_team_id=%s "
            "received_team_id=%s",
            channel.id,
            credential.slack_team_id,
            slack_team_id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Slack workspace does not "
                "match this channel."
            ),
        )


    # -----------------------------------------------------
    # Resolve Slack event
    # -----------------------------------------------------

    event = (
        payload.get(
            "event"
        )
        or {}
    )


    if not isinstance(
        event,
        dict,
    ):
        return {
            "ok":
                True,
        }


    event_type = (
        event.get(
            "type"
        )
    )


    logger.info(
        "Slack event received "
        "channel_id=%s "
        "team_id=%s "
        "event_id=%s "
        "event_type=%s "
        "channel_type=%s",
        channel.id,
        slack_team_id,
        payload.get(
            "event_id"
        ),
        event_type,
        event.get(
            "channel_type"
        ),
    )


    # -----------------------------------------------------
    # Ignore Slack retries
    # -----------------------------------------------------

    retry_number = (
        request.headers.get(
            "X-Slack-Retry-Num"
        )
    )


    if retry_number is not None:
        logger.info(
            "Ignoring Slack retry "
            "channel_id=%s "
            "team_id=%s "
            "event_id=%s "
            "retry=%s",
            channel.id,
            slack_team_id,
            payload.get(
                "event_id"
            ),
            retry_number,
        )

        return {
            "ok":
                True,
        }


    # -----------------------------------------------------
    # Ignore bot-generated events
    # -----------------------------------------------------

    if (
        event.get(
            "bot_id"
        )
        is not None
    ):
        logger.debug(
            "Ignoring Slack "
            "bot-generated event "
            "channel_id=%s "
            "team_id=%s",
            channel.id,
            slack_team_id,
        )

        return {
            "ok":
                True,
        }


    if (
        event.get(
            "subtype"
        )
        == "bot_message"
    ):
        return {
            "ok":
                True,
        }


    #
    # Some message subtypes represent
    # edits, deletes, joins, etc.
    #
    # We only want normal user messages
    # for DM processing.
    #
    if (
        event_type
        == "message"
        and event.get(
            "subtype"
        )
        is not None
    ):
        logger.debug(
            "Ignoring Slack message "
            "subtype "
            "channel_id=%s "
            "subtype=%s",
            channel.id,
            event.get(
                "subtype"
            ),
        )

        return {
            "ok":
                True,
        }


    # -----------------------------------------------------
    # app_mention
    # -----------------------------------------------------

    if (
        event_type
        == "app_mention"
    ):
        background_tasks.add_task(
            process_slack_event_background,
            slack_team_id,
            dict(
                event
            ),
        )


        logger.info(
            "Slack app_mention "
            "queued "
            "channel_id=%s "
            "team_id=%s "
            "event_id=%s",
            channel.id,
            slack_team_id,
            payload.get(
                "event_id"
            ),
        )


        return {
            "ok":
                True,
        }


    # -----------------------------------------------------
    # Direct message
    # -----------------------------------------------------

    if (
        event_type
        == "message"
        and event.get(
            "channel_type"
        )
        == "im"
    ):
        configuration = (
            channel.configuration
            or {}
        )


        if not bool(
            configuration.get(
                "respond_to_direct_messages",
                False,
            )
        ):
            logger.info(
                "Ignoring Slack DM "
                "because DMs are disabled "
                "channel_id=%s "
                "team_id=%s",
                channel.id,
                slack_team_id,
            )

            return {
                "ok":
                    True,
            }


        background_tasks.add_task(
            process_slack_dm_background,
            slack_team_id,
            dict(
                event
            ),
        )


        logger.info(
            "Slack direct message "
            "queued "
            "channel_id=%s "
            "team_id=%s "
            "event_id=%s "
            "slack_channel_id=%s",
            channel.id,
            slack_team_id,
            payload.get(
                "event_id"
            ),
            event.get(
                "channel"
            ),
        )


        return {
            "ok":
                True,
        }


    # -----------------------------------------------------
    # Unsupported event
    # -----------------------------------------------------

    logger.debug(
        "Ignoring unsupported Slack "
        "event "
        "channel_id=%s "
        "team_id=%s "
        "event_type=%s",
        channel.id,
        slack_team_id,
        event_type,
    )


    # -----------------------------------------------------
    # Always acknowledge Slack quickly
    # -----------------------------------------------------

    return {
        "ok":
            True,
    }