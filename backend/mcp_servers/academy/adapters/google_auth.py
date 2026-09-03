from __future__ import annotations

from google.oauth2 import service_account


SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"


def service_account_credentials(
    service_account_file: str,
    *,
    scopes: list[str],
):
    return service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes,
    )
