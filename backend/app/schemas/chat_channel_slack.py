from pydantic import (
    BaseModel,
    Field,
)


class ChatChannelSlackConnectRequest(
    BaseModel
):
    slack_team_id: str

    slack_team_name:str | None = None

    bot_user_id:str | None = None

    bot_token: str

    signing_secret: str

    respond_to_mentions: bool = True

    respond_to_direct_messages: bool = False

    allowed_slack_channel_ids:list[str] = Field(
            default_factory=list
        )


class ChatChannelSlackResponse(
    BaseModel
):
    slack_team_id: str

    slack_team_name: str | None

    bot_user_id: str | None

    configured: bool

    respond_to_mentions: bool

    respond_to_direct_messages: bool

    allowed_slack_channel_ids:list[str]