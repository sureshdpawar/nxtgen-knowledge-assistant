import hashlib
import io
import re

from pathlib import Path

from google.oauth2 import (
    service_account,
)
from googleapiclient.discovery import (
    build,
)
from googleapiclient.http import (
    MediaIoBaseDownload,
)

from app.core.config import (
    settings,
)
from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.sources.base import (
    KnowledgeSourceProvider,
)
from app.sources.source_item import (
    SourceItem,
)


class GoogleDriveProvider(
    KnowledgeSourceProvider
):

    DRIVE_SCOPE = (
        "https://www.googleapis.com/"
        "auth/drive.readonly"
    )

    FOLDER_MIME_TYPE = (
        "application/vnd.google-apps.folder"
    )

    GOOGLE_DOC_MIME_TYPE = (
        "application/vnd.google-apps.document"
    )

    GOOGLE_SHEET_MIME_TYPE = (
        "application/vnd.google-apps.spreadsheet"
    )

    GOOGLE_SLIDES_MIME_TYPE = (
        "application/vnd.google-apps.presentation"
    )

    PDF_MIME_TYPE = (
        "application/pdf"
    )

    TEXT_MIME_TYPES = {
        "text/plain",
        "text/markdown",
        "text/csv",
    }

    DEFAULT_RECURSIVE = True

    def discover(
        self,
        source: KnowledgeSource,
    ) -> list[SourceItem]:

        configuration = (
            source.configuration
            or {}
        )

        folder_id = (
            configuration.get(
                "folder_id"
            )
        )

        folder_url = (
            configuration.get(
                "folder_url"
            )
        )

        if (
            not folder_id
            and folder_url
        ):
            folder_id = (
                self._extract_folder_id(
                    folder_url
                )
            )

        if not folder_id:
            raise ValueError(
                "Google Drive source requires "
                "'folder_id' or 'folder_url'."
            )

        recursive = bool(
            configuration.get(
                "recursive",
                self.DEFAULT_RECURSIVE,
            )
        )

        drive = (
            self._build_drive_service()
        )

        self._verify_folder_access(
            drive=drive,
            folder_id=folder_id,
        )

        files = (
            self._discover_files(
                drive=drive,
                folder_id=folder_id,
                recursive=recursive,
            )
        )

        items: list[SourceItem] = []

        for file_metadata in files:

            item = (
                self._build_source_item(
                    drive=drive,
                    file_metadata=(
                        file_metadata
                    ),
                )
            )

            if item is None:
                continue

            items.append(
                item
            )

        return items

    def _build_drive_service(
        self,
    ):
        credential_file = (
            settings
            .GOOGLE_SERVICE_ACCOUNT_FILE
        )

        if not credential_file:
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_FILE "
                "is not configured."
            )

        credential_path = (
            Path(
                credential_file
            )
        )

        if not credential_path.is_absolute():
            credential_path = (
                settings.BASE_DIR
                / credential_path
            )

        if not credential_path.exists():
            raise RuntimeError(
                "Google service account "
                "credential file was not found: "
                f"{credential_path}"
            )

        credentials = (
            service_account
            .Credentials
            .from_service_account_file(
                str(
                    credential_path
                ),
                scopes=[
                    self.DRIVE_SCOPE
                ],
            )
        )

        return build(
            "drive",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

    def _verify_folder_access(
        self,
        drive,
        folder_id: str,
    ) -> None:

        try:
            metadata = (
                drive.files()
                .get(
                    fileId=folder_id,
                    fields=(
                        "id,name,mimeType,"
                        "trashed"
                    ),
                    supportsAllDrives=True,
                )
                .execute()
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to access Google Drive "
                f"folder '{folder_id}'. "
                "Make sure the folder is shared "
                "with the configured service "
                "account."
            ) from exc

        if metadata.get(
            "trashed"
        ):
            raise RuntimeError(
                "The configured Google Drive "
                "folder is in Trash."
            )

        if (
            metadata.get(
                "mimeType"
            )
            != self.FOLDER_MIME_TYPE
        ):
            raise ValueError(
                "The configured Google Drive "
                "ID is not a folder."
            )

    def _discover_files(
        self,
        drive,
        folder_id: str,
        recursive: bool,
    ) -> list[dict]:

        discovered: list[dict] = []

        pending_folders = [
            folder_id
        ]

        visited_folders: set[str] = (
            set()
        )

        while pending_folders:

            current_folder_id = (
                pending_folders.pop(0)
            )

            if (
                current_folder_id
                in visited_folders
            ):
                continue

            visited_folders.add(
                current_folder_id
            )

            children = (
                self._list_folder_children(
                    drive=drive,
                    folder_id=(
                        current_folder_id
                    ),
                )
            )

            for child in children:

                mime_type = (
                    child.get(
                        "mimeType"
                    )
                )

                if (
                    mime_type
                    == self.FOLDER_MIME_TYPE
                ):
                    if recursive:
                        pending_folders.append(
                            child["id"]
                        )

                    continue

                discovered.append(
                    child
                )

        return discovered

    def _list_folder_children(
        self,
        drive,
        folder_id: str,
    ) -> list[dict]:

        result: list[dict] = []

        page_token = None

        while True:

            response = (
                drive.files()
                .list(
                    q=(
                        f"'{folder_id}' "
                        "in parents "
                        "and trashed = false"
                    ),
                    fields=(
                        "nextPageToken,"
                        "files("
                        "id,"
                        "name,"
                        "mimeType,"
                        "modifiedTime,"
                        "size,"
                        "md5Checksum,"
                        "webViewLink,"
                        "parents"
                        ")"
                    ),
                    pageToken=page_token,
                    pageSize=1000,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )

            result.extend(
                response.get(
                    "files",
                    [],
                )
            )

            page_token = (
                response.get(
                    "nextPageToken"
                )
            )

            if not page_token:
                break

        return result

    def _build_source_item(
        self,
        drive,
        file_metadata: dict,
    ) -> SourceItem | None:

        file_id = (
            file_metadata["id"]
        )

        name = (
            file_metadata.get(
                "name"
            )
            or file_id
        )

        mime_type = (
            file_metadata.get(
                "mimeType",
                "",
            )
        )

        source_url = (
            file_metadata.get(
                "webViewLink"
            )
            or (
                "https://drive.google.com/"
                f"open?id={file_id}"
            )
        )

        if (
            mime_type
            == self.GOOGLE_DOC_MIME_TYPE
        ):
            content = (
                self._export_google_doc(
                    drive=drive,
                    file_id=file_id,
                )
            )

            filename = (
                self._ensure_extension(
                    name,
                    ".txt",
                )
            )

            output_mime_type = (
                "text/plain"
            )

        elif (
            mime_type
            == self.PDF_MIME_TYPE
        ):
            content = (
                self._download_file(
                    drive=drive,
                    file_id=file_id,
                )
            )

            filename = (
                self._ensure_extension(
                    name,
                    ".pdf",
                )
            )

            output_mime_type = (
                "application/pdf"
            )

        elif (
            mime_type
            in self.TEXT_MIME_TYPES
        ):
            content = (
                self._download_file(
                    drive=drive,
                    file_id=file_id,
                )
            )

            filename = (
                self._normalize_text_filename(
                    name=name,
                    mime_type=mime_type,
                )
            )

            output_mime_type = (
                mime_type
            )

        else:
            #
            # MVP:
            # Skip unsupported file types
            # instead of failing the whole
            # Google Drive sync.
            #
            return None

        checksum = (
            hashlib.sha256(
                content
            )
            .hexdigest()
        )

        return SourceItem(
            external_id=file_id,
            title=name,
            mime_type=(
                output_mime_type
            ),
            checksum=checksum,
            source_url=source_url,
            filename=filename,
            metadata={
                "source_type":
                    "GOOGLE_DRIVE",

                "google_drive_file_id":
                    file_id,

                "google_drive_mime_type":
                    mime_type,

                "modified_time":
                    file_metadata.get(
                        "modifiedTime"
                    ),

                "original_name":
                    name,

                "web_view_link":
                    source_url,
            },
            content=content,
        )

    def _download_file(
        self,
        drive,
        file_id: str,
    ) -> bytes:

        request = (
            drive.files()
            .get_media(
                fileId=file_id,
                supportsAllDrives=True,
            )
        )

        buffer = (
            io.BytesIO()
        )

        downloader = (
            MediaIoBaseDownload(
                buffer,
                request,
            )
        )

        done = False

        while not done:
            _, done = (
                downloader.next_chunk()
            )

        return (
            buffer.getvalue()
        )

    def _export_google_doc(
        self,
        drive,
        file_id: str,
    ) -> bytes:

        request = (
            drive.files()
            .export_media(
                fileId=file_id,
                mimeType="text/plain",
            )
        )

        buffer = (
            io.BytesIO()
        )

        downloader = (
            MediaIoBaseDownload(
                buffer,
                request,
            )
        )

        done = False

        while not done:
            _, done = (
                downloader.next_chunk()
            )

        return (
            buffer.getvalue()
        )

    def _extract_folder_id(
        self,
        folder_url: str,
    ) -> str:

        folder_url = (
            folder_url.strip()
        )

        patterns = [
            r"/folders/([^/?#]+)",
            r"[?&]id=([^&#]+)",
        ]

        for pattern in patterns:

            match = (
                re.search(
                    pattern,
                    folder_url,
                )
            )

            if match:
                return (
                    match.group(1)
                )

        #
        # Also allow a raw folder ID
        # to be entered into the URL
        # field.
        #
        if (
            "/" not in folder_url
            and "?" not in folder_url
        ):
            return folder_url

        raise ValueError(
            "Unable to determine Google "
            "Drive folder ID from the "
            "provided URL."
        )

    def _ensure_extension(
        self,
        filename: str,
        extension: str,
    ) -> str:

        if (
            filename
            .lower()
            .endswith(
                extension.lower()
            )
        ):
            return filename

        return (
            f"{filename}{extension}"
        )

    def _normalize_text_filename(
        self,
        name: str,
        mime_type: str,
    ) -> str:

        lower_name = (
            name.lower()
        )

        if mime_type == "text/markdown":

            if lower_name.endswith(
                ".md"
            ):
                return name

            return (
                f"{name}.md"
            )

        #
        # CSV is converted to .txt for
        # ingestion because the existing
        # text parser already handles it
        # as textual knowledge.
        #
        if mime_type == "text/csv":

            if lower_name.endswith(
                ".csv"
            ):
                stem = (
                    name[:-4]
                )

                return (
                    f"{stem}.txt"
                )

            return (
                f"{name}.txt"
            )

        if lower_name.endswith(
            ".txt"
        ):
            return name

        return (
            f"{name}.txt"
        )