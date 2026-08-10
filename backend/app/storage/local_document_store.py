from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class LocalDocumentStore:

    def save(
        self,
        storage_key: str,
        file: UploadFile,
    ) -> None:

        full_path = (
            Path(settings.DOCUMENT_STORAGE_PATH)
            / storage_key
        )

        full_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.file.seek(0)

        with full_path.open("wb") as buffer:
            buffer.write(file.file.read())

        file.file.seek(0)

    def delete(
        self,
        storage_key: str,
    ) -> None:

        full_path = (
            Path(settings.DOCUMENT_STORAGE_PATH)
            / storage_key
        )

        if full_path.exists():
            full_path.unlink()

    def exists(
        self,
        storage_key: str,
    ) -> bool:

        return (
            Path(settings.DOCUMENT_STORAGE_PATH)
            / storage_key
        ).exists()