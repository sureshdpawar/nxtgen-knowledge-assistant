from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from mcp_servers.academy.config import AcademyMCPSettings
from mcp_servers.academy.services.enquiry_service import (
    AcademyEnquiryService,
)


mcp = FastMCP(
    "NXTGEN Academy MCP",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "mcp",
            "mcp:9000",
            "localhost",
            "localhost:9000",
            "127.0.0.1",
            "127.0.0.1:9000",
        ],
        allowed_origins=[
            "http://mcp",
            "http://mcp:9000",
            "http://localhost",
            "http://localhost:9000",
            "http://127.0.0.1",
            "http://127.0.0.1:9000",
        ],
    ),
)


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