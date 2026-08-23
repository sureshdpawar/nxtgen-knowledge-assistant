import shutil
import subprocess
import tempfile

from pathlib import Path


class OfficeFormatNormalizer:
    """
    Converts legacy Microsoft Office formats
    into modern OOXML formats using LibreOffice.

    .doc -> .docx
    .ppt -> .pptx
    .xls -> .xlsx

    Modern formats are returned unchanged.
    """

    LEGACY_EXTENSION_MAP = {
        ".doc": ".docx",
        ".ppt": ".pptx",
        ".xls": ".xlsx",
    }

    MODERN_EXTENSIONS = {
        ".docx",
        ".pptx",
        ".xlsx",
    }

    def normalize(
        self,
        file_path: Path,
    ) -> Path:

        file_path = (
            Path(
                file_path
            )
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Office file not found: "
                f"{file_path}"
            )

        extension = (
            file_path
            .suffix
            .lower()
        )

        if (
            extension
            in self.MODERN_EXTENSIONS
        ):
            return file_path

        target_extension = (
            self.LEGACY_EXTENSION_MAP
            .get(
                extension
            )
        )

        if not target_extension:
            return file_path

        soffice = (
            self._find_soffice()
        )

        if soffice is None:
            raise RuntimeError(
                "LibreOffice is required to "
                f"process legacy Office file "
                f"'{file_path.name}'. "
                "Install LibreOffice and ensure "
                "'soffice' is available."
            )

        temp_directory = Path(
            tempfile.mkdtemp(
                prefix="nxtgen-office-"
            )
        )

        try:
            input_copy = (
                temp_directory
                / file_path.name
            )

            shutil.copy2(
                file_path,
                input_copy,
            )

            target_format = (
                target_extension
                .lstrip(".")
            )

            command = [
                str(
                    soffice
                ),
                "--headless",
                "--convert-to",
                target_format,
                "--outdir",
                str(
                    temp_directory
                ),
                str(
                    input_copy
                ),
            ]

            process = (
                subprocess.run(
                    command,
                    stdout=(
                        subprocess.PIPE
                    ),
                    stderr=(
                        subprocess.PIPE
                    ),
                    text=True,
                    timeout=120,
                    check=False,
                )
            )

            if (
                process.returncode
                != 0
            ):
                raise RuntimeError(
                    "LibreOffice conversion "
                    "failed for "
                    f"'{file_path.name}'. "
                    f"stdout={process.stdout!r} "
                    f"stderr={process.stderr!r}"
                )

            converted_path = (
                temp_directory
                / (
                    input_copy.stem
                    + target_extension
                )
            )

            if not converted_path.exists():

                candidates = list(
                    temp_directory.glob(
                        f"*{target_extension}"
                    )
                )

                if len(candidates) == 1:
                    converted_path = (
                        candidates[0]
                    )

            if not converted_path.exists():
                raise RuntimeError(
                    "LibreOffice completed but "
                    "the converted file was not "
                    "created for "
                    f"'{file_path.name}'. "
                    f"stdout={process.stdout!r}"
                )

            #
            # Store converted file next to
            # original processing file.
            #
            destination = (
                file_path
                .with_suffix(
                    target_extension
                )
            )

            shutil.copy2(
                converted_path,
                destination,
            )

            return destination

        finally:
            shutil.rmtree(
                temp_directory,
                ignore_errors=True,
            )

    def requires_conversion(
        self,
        file_path: Path,
    ) -> bool:

        return (
            Path(
                file_path
            )
            .suffix
            .lower()
            in self.LEGACY_EXTENSION_MAP
        )

    def _find_soffice(
        self,
    ) -> Path | None:

        #
        # Linux / Docker
        #
        executable = (
            shutil.which(
                "soffice"
            )
        )

        if executable:
            return Path(
                executable
            )

        executable = (
            shutil.which(
                "libreoffice"
            )
        )

        if executable:
            return Path(
                executable
            )

        #
        # Standard macOS LibreOffice path.
        #
        mac_path = Path(
            "/Applications/"
            "LibreOffice.app/"
            "Contents/MacOS/"
            "soffice"
        )

        if mac_path.exists():
            return mac_path

        return None