from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from mcp_servers.academy.config import AcademyMCPSettings
from mcp_servers.academy.services.enquiry_service import (
    AcademyEnquiryService,
)


mcp = FastMCP(
    "NXTGEN Academy MCP",
    stateless_http=True,
    json_response=True,
)


@lru_cache(maxsize=1)
def _service() -> AcademyEnquiryService:
    return AcademyEnquiryService(
        AcademyMCPSettings.from_env()
    )


@mcp.tool()
def create_enquiry(
    name: str,
    phone: str,
    email: str | None = None,
) -> dict:
    """Create an academy enquiry for a prospective learner."""
    return _service().create_enquiry(
        name=name,
        phone=phone,
        email=email,
    )


@mcp.tool()
def update_enquiry(
    enquiry_id: str,
    callback_required: bool,
    email: str | None = None,
) -> dict:
    """Update callback intent and optional email for an existing enquiry."""
    return _service().update_enquiry(
        enquiry_id=enquiry_id,
        callback_required=callback_required,
        email=email,
    )


@mcp.tool()
def schedule_consultation(
    enquiry_id: str,
    email: str,
    start_time: str,
) -> dict:
    """Schedule an academy consultation and create a Google Meet invitation."""
    return _service().schedule_consultation(
        enquiry_id=enquiry_id,
        email=email,
        start_time=start_time,
    )


app = mcp.streamable_http_app()
