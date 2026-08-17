from mcp.server.fastmcp import (
    FastMCP,
)


mcp = FastMCP(
    "NXTGEN Procurement MCP",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def get_vendor(
    vendor_id: str,
) -> dict:
    vendors = {
        "V-100": {
            "vendor_id":
                "V-100",

            "name":
                "Acme Hardware",

            "status":
                "ACTIVE",

            "risk":
                "LOW",
        },

        "V-200": {
            "vendor_id":
                "V-200",

            "name":
                "Northwind Services",

            "status":
                "ACTIVE",

            "risk":
                "MEDIUM",
        },
    }

    normalized_id = (
        vendor_id
        .strip()
        .upper()
    )

    vendor = vendors.get(
        normalized_id,
    )

    if vendor is None:
        return {
            "found":
                False,

            "vendor_id":
                normalized_id,

            "message":
                "Vendor not found.",
        }

    return {
        "found":
            True,

        "vendor":
            vendor,
    }


@mcp.tool()
def get_vendor_risk(
    vendor_id: str,
) -> dict:
    risks = {
        "V-100":
            "LOW",

        "V-200":
            "MEDIUM",

        "V-300":
            "HIGH",
    }

    normalized_id = (
        vendor_id
        .strip()
        .upper()
    )

    return {
        "vendor_id":
            normalized_id,

        "risk":
            risks.get(
                normalized_id,
                "UNKNOWN",
            ),
    }


#
# Expose MCP as ASGI.
#
app = (
    mcp.streamable_http_app()
)