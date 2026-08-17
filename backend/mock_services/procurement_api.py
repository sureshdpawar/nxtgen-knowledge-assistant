from fastapi import (
    FastAPI,
    HTTPException,
)


app = FastAPI(
    title=(
        "NXTGEN Mock "
        "Procurement API"
    ),
    version="1.0.0",
)


PURCHASE_ORDERS = {
    "PO-10482": {
        "purchase_order_id":
            "PO-10482",

        "vendor":
            "Acme Hardware",

        "amount":
            18420,

        "currency":
            "USD",

        "status":
            "PENDING_FINANCE",

        "department":
            "Engineering",
    },

    "PO-20001": {
        "purchase_order_id":
            "PO-20001",

        "vendor":
            "Northwind Services",

        "amount":
            2300,

        "currency":
            "USD",

        "status":
            "APPROVED",

        "department":
            "IT",
    },

    "PO-30015": {
        "purchase_order_id":
            "PO-30015",

        "vendor":
            "Contoso Consulting",

        "amount":
            42750,

        "currency":
            "USD",

        "status":
            "REJECTED",

        "department":
            "Finance",
    },
}


@app.get(
    "/health",
)
def health():
    return {
        "status": "ok",
    }


@app.get(
    "/purchase-orders/{purchase_order_id}",
)
def get_purchase_order(
    purchase_order_id: str,
):
    normalized_id = (
        purchase_order_id
        .strip()
        .upper()
    )

    purchase_order = (
        PURCHASE_ORDERS.get(
            normalized_id,
        )
    )

    if purchase_order is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Purchase order "
                "not found."
            ),
        )

    return purchase_order