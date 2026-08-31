from __future__ import annotations

from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)


class WebsiteURLCanonicalizer:
    """
    Canonicalizes website URLs for crawl identity.

    This component answers:

        "Do these URLs represent the same logical crawl resource?"

    It deliberately does not:
    - fetch URLs
    - inspect HTML
    - decide crawl scope
    - apply customer-specific URL rules
    - remove arbitrary query parameters

    Unknown/business query parameters are preserved. Only well-known
    tracking parameters are removed.
    """

    TRACKING_QUERY_PARAMETERS = {
        "dclid",
        "fbclid",
        "gad_source",
        "gclid",
        "gbraid",
        "igshid",
        "li_fat_id",
        "mc_cid",
        "mc_eid",
        "msclkid",
        "ttclid",
        "twclid",
        "vero_conv",
        "vero_id",
        "wbraid",
        "_ga",
        "_gl",
        "_hsenc",
        "_hsmi",
    }

    TRACKING_QUERY_PREFIXES = (
        "utm_",
        "hsa_",
    )

    INDEX_DOCUMENTS = {
        "index.html",
        "index.htm",
    }

    SUPPORTED_SCHEMES = {
        "http",
        "https",
    }

    def canonicalize(
        self,
        url: str,
        base_url: str | None = None,
    ) -> str:
        value = url.strip()

        if not value:
            raise ValueError(
                "Website URL cannot be empty."
            )

        if base_url is not None:
            value = urljoin(
                base_url,
                value,
            )

        parsed = urlsplit(
            value
        )

        if not parsed.scheme:
            value = (
                f"https://{value}"
            )

            parsed = urlsplit(
                value
            )

        scheme = (
            parsed.scheme.lower()
        )

        if (
            scheme
            not in self.SUPPORTED_SCHEMES
        ):
            raise ValueError(
                "Website URL must use "
                "http or https."
            )

        if not parsed.hostname:
            raise ValueError(
                "Website URL must contain "
                "a hostname."
            )

        hostname = (
            parsed.hostname.lower()
        )

        netloc = (
            self._normalize_netloc(
                scheme=scheme,
                hostname=hostname,
                port=parsed.port,
            )
        )

        path = (
            self._normalize_path(
                parsed.path
            )
        )

        query = (
            self._normalize_query(
                parsed.query
            )
        )

        return urlunsplit(
            (
                scheme,
                netloc,
                path,
                query,
                "",
            )
        )

    def same_resource(
        self,
        first_url: str,
        second_url: str,
    ) -> bool:
        return (
            self.canonicalize(
                first_url
            )
            == self.canonicalize(
                second_url
            )
        )

    def _normalize_netloc(
        self,
        scheme: str,
        hostname: str,
        port: int | None,
    ) -> str:
        if (
            scheme == "http"
            and port == 80
        ):
            port = None

        if (
            scheme == "https"
            and port == 443
        ):
            port = None

        serialized_host = hostname

        if (
            ":" in hostname
            and not hostname.startswith("[")
        ):
            serialized_host = (
                f"[{hostname}]"
            )

        if port is None:
            return serialized_host

        return (
            f"{serialized_host}:{port}"
        )

    def _normalize_path(
        self,
        path: str,
    ) -> str:
        normalized = (
            path
            or "/"
        )

        if (
            normalized != "/"
            and normalized.endswith("/")
        ):
            normalized = (
                normalized.rstrip("/")
            )

        segments = (
            normalized.split("/")
        )

        if (
            segments
            and segments[-1].lower()
            in self.INDEX_DOCUMENTS
        ):
            segments = (
                segments[:-1]
            )

            normalized = (
                "/".join(
                    segments
                )
            )

            if not normalized:
                normalized = "/"

            if (
                normalized != "/"
                and normalized.endswith("/")
            ):
                normalized = (
                    normalized.rstrip("/")
                )

        if not normalized.startswith("/"):
            normalized = (
                f"/{normalized}"
            )

        return normalized

    def _normalize_query(
        self,
        query: str,
    ) -> str:
        if not query:
            return ""

        parameters = parse_qsl(
            query,
            keep_blank_values=True,
        )

        retained = []

        for key, value in parameters:
            if self._is_tracking_parameter(
                key
            ):
                continue

            retained.append(
                (
                    key,
                    value,
                )
            )

        retained.sort(
            key=lambda item: (
                item[0],
                item[1],
            )
        )

        return urlencode(
            retained,
            doseq=True,
        )

    def _is_tracking_parameter(
        self,
        name: str,
    ) -> bool:
        normalized = (
            name.lower()
        )

        if (
            normalized
            in self.TRACKING_QUERY_PARAMETERS
        ):
            return True

        return any(
            normalized.startswith(
                prefix
            )
            for prefix
            in self.TRACKING_QUERY_PREFIXES
        )
