import hashlib
from pathlib import Path

from fastapi import UploadFile


def extension(
    filename: str,
) -> str:

    return Path(filename).suffix.lower()


def checksum(
    file: UploadFile,
) -> str:

    sha = hashlib.sha256()

    file.file.seek(0)

    while chunk := file.file.read(8192):
        sha.update(chunk)

    file.file.seek(0)

    return sha.hexdigest()