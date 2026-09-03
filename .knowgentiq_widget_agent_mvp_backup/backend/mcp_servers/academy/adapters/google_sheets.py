from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from googleapiclient.discovery import build

from mcp_servers.academy.adapters.google_auth import (
    SHEETS_SCOPE,
    service_account_credentials,
)
from mcp_servers.academy.config import AcademyMCPSettings


HEADERS = [
    "Enquiry ID",
    "Name",
    "Phone",
    "Email",
    "Callback",
    "Meeting",
    "Status",
    "Created At",
    "Updated At",
]


class GoogleSheetsEnquiryAdapter:
    def __init__(self, settings: AcademyMCPSettings):
        self.settings = settings
        credentials = service_account_credentials(
            settings.google_service_account_file,
            scopes=[SHEETS_SCOPE],
        )
        self.service = build(
            "sheets",
            "v4",
            credentials=credentials,
            cache_discovery=False,
        )

    def ensure_headers(self) -> None:
        range_name = (
            f"{self.settings.enquiry_sheet_name}!A1:I1"
        )
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=(
                    self.settings.enquiry_spreadsheet_id
                ),
                range=range_name,
            )
            .execute()
        )
        values = result.get("values", [])

        if values and values[0] == HEADERS:
            return

        (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=(
                    self.settings.enquiry_spreadsheet_id
                ),
                range=range_name,
                valueInputOption="RAW",
                body={"values": [HEADERS]},
            )
            .execute()
        )

    def append_enquiry(
        self,
        *,
        enquiry_id: str,
        name: str,
        phone: str,
        email: str | None = None,
    ) -> None:
        self.ensure_headers()

        now = datetime.now(
            timezone.utc
        ).isoformat()

        normalized_email = (
            email.strip()
            if email
            else ""
        )

        row = [
            enquiry_id,
            name,
            phone,
            normalized_email,
            "NO",
            "",
            "NEW",
            now,
            now,
        ]

        (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=(
                    self.settings.enquiry_spreadsheet_id
                ),
                range=(
                    f"{self.settings.enquiry_sheet_name}"
                    "!A:I"
                ),
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            )
            .execute()
        )

    def find_row(
        self,
        enquiry_id: str,
    ) -> tuple[int, list[str]] | None:
        self.ensure_headers()

        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=(
                    self.settings.enquiry_spreadsheet_id
                ),
                range=(
                    f"{self.settings.enquiry_sheet_name}"
                    "!A2:I"
                ),
            )
            .execute()
        )

        rows = result.get("values", [])

        for offset, row in enumerate(
            rows,
            start=2,
        ):
            if (
                row
                and str(row[0]).strip()
                == enquiry_id
            ):
                padded = (
                    list(row)
                    + [""] * (
                        len(HEADERS)
                        - len(row)
                    )
                )
                return (
                    offset,
                    padded[: len(HEADERS)],
                )

        return None

    def get_enquiry(
        self,
        enquiry_id: str,
    ) -> dict[str, Any] | None:
        found = self.find_row(
            enquiry_id
        )

        if found is None:
            return None

        _, row = found

        return dict(
            zip(
                HEADERS,
                row,
                strict=True,
            )
        )

    def update_enquiry(
        self,
        enquiry_id: str,
        *,
        callback_required: bool | None = None,
        email: str | None = None,
        meeting: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        found = self.find_row(
            enquiry_id
        )

        if found is None:
            return None

        row_number, row = found

        if email is not None:
            row[3] = email

        if callback_required is not None:
            row[4] = (
                "YES"
                if callback_required
                else "NO"
            )

        if meeting is not None:
            row[5] = meeting

        if status is not None:
            row[6] = status

        row[8] = datetime.now(
            timezone.utc
        ).isoformat()

        (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=(
                    self.settings.enquiry_spreadsheet_id
                ),
                range=(
                    f"{self.settings.enquiry_sheet_name}"
                    f"!A{row_number}:I{row_number}"
                ),
                valueInputOption="RAW",
                body={"values": [row]},
            )
            .execute()
        )

        return dict(
            zip(
                HEADERS,
                row,
                strict=True,
            )
        )
