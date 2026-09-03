from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from mcp_servers.academy.adapters.google_auth import (
    CALENDAR_SCOPE,
    service_account_credentials,
)
from mcp_servers.academy.config import AcademyMCPSettings


class GoogleCalendarAdapter:
    def __init__(self, settings: AcademyMCPSettings):
        self.settings = settings
        credentials = service_account_credentials(
            settings.google_service_account_file,
            scopes=[CALENDAR_SCOPE],
        )
        self.service = build(
            "calendar",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

    def _parse_start_time(self, start_time: str) -> datetime:
        normalized = start_time.strip().replace("Z", "+00:00")
        value = datetime.fromisoformat(normalized)
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo(self.settings.timezone))
        return value

    def schedule_consultation(
        self,
        *,
        enquiry_id: str,
        visitor_name: str,
        visitor_email: str,
        start_time: str,
    ) -> dict:
        start = self._parse_start_time(start_time)
        end = start + timedelta(
            minutes=self.settings.consultation_duration_minutes
        )

        attendees = [{"email": visitor_email}]
        if self.settings.academy_attendee_email:
            attendees.append({"email": self.settings.academy_attendee_email})

        body = {
            "summary": f"Academy Consultation - {visitor_name}",
            "description": f"Knowgentiq academy enquiry: {enquiry_id}",
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": self.settings.timezone,
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": self.settings.timezone,
            },
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        event = (
            self.service.events()
            .insert(
                calendarId=self.settings.calendar_id,
                body=body,
                conferenceDataVersion=1,
                sendUpdates="all",
            )
            .execute()
        )

        meet_url = event.get("hangoutLink")
        if not meet_url:
            for entry_point in (
                event.get("conferenceData", {}).get("entryPoints", [])
            ):
                if entry_point.get("entryPointType") == "video":
                    meet_url = entry_point.get("uri")
                    break

        return {
            "event_id": event.get("id"),
            "event_url": event.get("htmlLink"),
            "meet_url": meet_url,
            "start_time": event.get("start", {}).get("dateTime"),
            "end_time": event.get("end", {}).get("dateTime"),
            "status": event.get("status"),
        }
