from __future__ import annotations

from uuid import uuid4

from mcp_servers.academy.adapters.google_calendar import (
    GoogleCalendarAdapter,
)
from mcp_servers.academy.adapters.google_sheets import (
    GoogleSheetsEnquiryAdapter,
)
from mcp_servers.academy.config import AcademyMCPSettings


class AcademyEnquiryService:
    def __init__(self, settings: AcademyMCPSettings):
        self.settings = settings
        self.sheets = GoogleSheetsEnquiryAdapter(
            settings
        )
        self._calendar = None

    @property
    def calendar(self) -> GoogleCalendarAdapter:
        if self._calendar is None:
            self._calendar = GoogleCalendarAdapter(
                self.settings
            )

        return self._calendar

    def create_enquiry(
        self,
        *,
        name: str,
        phone: str,
        email: str | None = None,
    ) -> dict:
        normalized_name = name.strip()
        normalized_phone = phone.strip()
        normalized_email = (
            email.strip()
            if email
            else None
        )

        if not normalized_name:
            raise ValueError("name is required")

        if not normalized_phone:
            raise ValueError("phone is required")

        enquiry_id = str(uuid4())

        self.sheets.append_enquiry(
            enquiry_id=enquiry_id,
            name=normalized_name,
            phone=normalized_phone,
            email=normalized_email,
        )

        return {
            "success": True,
            "enquiry_id": enquiry_id,
            "status": "NEW",
        }

    def update_enquiry(
        self,
        *,
        enquiry_id: str,
        callback_required: bool,
        email: str | None = None,
    ) -> dict:
        updated = self.sheets.update_enquiry(
            enquiry_id.strip(),
            callback_required=callback_required,
            email=(
                email.strip()
                if email
                else None
            ),
            status=(
                "CALLBACK_REQUESTED"
                if callback_required
                else "OPEN"
            ),
        )

        if updated is None:
            return {
                "success": False,
                "enquiry_id": enquiry_id,
                "message": "Enquiry not found.",
            }

        return {
            "success": True,
            "enquiry_id": enquiry_id,
            "callback_required":
                callback_required,
            "email":
                updated.get("Email")
                or None,
            "status":
                updated.get("Status"),
        }

    def schedule_consultation(
        self,
        *,
        enquiry_id: str,
        email: str,
        start_time: str,
    ) -> dict:
        enquiry = self.sheets.get_enquiry(
            enquiry_id.strip()
        )

        if enquiry is None:
            return {
                "success": False,
                "enquiry_id": enquiry_id,
                "message": "Enquiry not found.",
            }

        normalized_email = email.strip()

        if not normalized_email:
            raise ValueError("email is required")

        meeting = self.calendar.schedule_consultation(
            enquiry_id=enquiry_id,
            visitor_name=(
                enquiry.get("Name")
                or "Prospective Learner"
            ),
            visitor_email=normalized_email,
            start_time=start_time,
        )

        meeting_reference = (
            meeting.get("meet_url")
            or meeting.get("event_url")
            or meeting.get("event_id")
            or "scheduled"
        )

        self.sheets.update_enquiry(
            enquiry_id,
            callback_required=True,
            email=normalized_email,
            meeting=str(meeting_reference),
            status="CONSULTATION_SCHEDULED",
        )

        return {
            "success": True,
            "enquiry_id": enquiry_id,
            "meeting": meeting,
            "status": "CONSULTATION_SCHEDULED",
        }
