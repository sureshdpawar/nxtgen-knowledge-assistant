from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AcademyMCPSettings:
    google_service_account_file: str
    enquiry_spreadsheet_id: str
    enquiry_sheet_name: str
    calendar_id: str
    academy_attendee_email: str | None
    timezone: str
    consultation_duration_minutes: int

    @classmethod
    def from_env(cls) -> "AcademyMCPSettings":
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        spreadsheet_id = os.getenv("ACADEMY_ENQUIRY_SPREADSHEET_ID")

        if not service_account_file:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is required")

        if not spreadsheet_id:
            raise RuntimeError("ACADEMY_ENQUIRY_SPREADSHEET_ID is required")

        return cls(
            google_service_account_file=service_account_file,
            enquiry_spreadsheet_id=spreadsheet_id,
            enquiry_sheet_name=os.getenv("ACADEMY_ENQUIRY_SHEET_NAME", "Enquiries"),
            calendar_id=os.getenv("ACADEMY_CALENDAR_ID", "primary"),
            academy_attendee_email=os.getenv("ACADEMY_ATTENDEE_EMAIL") or None,
            timezone=os.getenv("ACADEMY_TIMEZONE", "Asia/Kolkata"),
            consultation_duration_minutes=int(
                os.getenv("ACADEMY_CONSULTATION_DURATION_MINUTES", "30")
            ),
        )
