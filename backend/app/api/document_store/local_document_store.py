from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class LocalDocumentStore:

    def save(
        self,
        path: str,
        file: UploadFile,
    ) -> None:

        target = Path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with target.open("wb") as buffer:
            buffer.write(
                file.file.read()
            )