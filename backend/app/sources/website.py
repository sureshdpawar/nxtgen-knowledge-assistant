import hashlib
import html
import re

from collections import deque
from html.parser import HTMLParser
from urllib.parse import (
    urldefrag,
    urljoin,
    urlparse,
    urlunparse,
)

import httpx

from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.sources.base import (
    KnowledgeSourceProvider,
)
from app.sources.source_item import (
    SourceItem,
)


class WebsiteHTMLParser(
    HTMLParser
):

    SKIPPED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
    }

    def __init__(self):
        super().__init__()

        self._skip_depth = 0

        self._text_parts: list[str] = []

        self.links: list[str] = []

        self.title_parts: list[str] = []

        self._inside_title = False

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:

        tag = tag.lower()

        if tag in self.SKIPPED_TAGS:
            self._skip_depth += 1
            return

        if tag == "title":
            self._inside_title = True

        if (
            tag == "a"
            and self._skip_depth == 0
        ):
            href = dict(
                attrs
            ).get(
                "href"
            )

            if href:
                self.links.append(
                    href
                )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:

        tag = tag.lower()

        if tag in self.SKIPPED_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1

            return

        if tag == "title":
            self._inside_title = False

    def handle_data(
        self,
        data: str,
    ) -> None:

        if self._skip_depth > 0:
            return

        value = (
            html.unescape(
                data
            )
            .strip()
        )

        if not value:
            return

        if self._inside_title:
            self.title_parts.append(
                value
            )

        self._text_parts.append(
            value
        )

    def get_text(
        self,
    ) -> str:

        text = "\n".join(
            self._text_parts
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def get_title(
        self,
    ) -> str:

        return " ".join(
            self.title_parts
        ).strip()


class WebsiteProvider(
    KnowledgeSourceProvider
):

    DEFAULT_MAX_PAGES = 50

    DEFAULT_MAX_DEPTH = 2

    DEFAULT_TIMEOUT_SECONDS = 15.0

    USER_AGENT = (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )

    def discover(
        self,
        source: KnowledgeSource,
    ) -> list[SourceItem]:

        configuration = (
            source.configuration
            or {}
        )

        base_url = (
            configuration
            .get(
                "base_url"
            )
            or configuration
            .get(
                "url"
            )
        )

        if not base_url:
            raise ValueError(
                "Website source requires "
                "'base_url' in configuration."
            )

        base_url = (
            self._normalize_url(
                base_url
            )
        )

        max_pages = int(
            configuration.get(
                "max_pages",
                self.DEFAULT_MAX_PAGES,
            )
        )

        max_depth = int(
            configuration.get(
                "max_depth",
                self.DEFAULT_MAX_DEPTH,
            )
        )

        include_patterns = (
            configuration.get(
                "include_patterns",
                [],
            )
            or []
        )

        exclude_patterns = (
            configuration.get(
                "exclude_patterns",
                [],
            )
            or []
        )

        base_host = (
            self._canonical_host(
                base_url
            )
        )

        queue = deque(
            [
                (
                    base_url,
                    0,
                )
            ]
        )

        queued_urls = {
            base_url
        }

        visited_urls: set[str] = set()

        discovered_urls: set[str] = set()

        items: list[SourceItem] = []

        with httpx.Client(
            follow_redirects=True,
            timeout=(
                self.DEFAULT_TIMEOUT_SECONDS
            ),
            headers={
                "User-Agent":
                    self.USER_AGENT,

                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "image/avif,"
                    "image/webp,"
                    "*/*;q=0.8"
                ),

                "Accept-Language":
                    "en-US,en;q=0.9",

                "Cache-Control":
                    "no-cache",

                "Pragma":
                    "no-cache",
            },
        ) as client:

            while (
                queue
                and len(items)
                < max_pages
            ):
                (
                    current_url,
                    depth,
                ) = queue.popleft()

                queued_urls.discard(
                    current_url
                )

                if (
                    current_url
                    in visited_urls
                ):
                    continue

                visited_urls.add(
                    current_url
                )

                if not self._should_include(
                    current_url,
                    include_patterns,
                    exclude_patterns,
                ):
                    continue

                try:
                    response = client.get(
                        current_url
                    )

                    response.raise_for_status()

                except httpx.HTTPStatusError as exc:

                    if depth == 0:
                        raise RuntimeError(
                            "Website could not be fetched. "
                            f"HTTP "
                            f"{exc.response.status_code} "
                            f"from {current_url}."
                        ) from exc

                    continue

                except httpx.HTTPError as exc:

                    if depth == 0:
                        raise RuntimeError(
                            "Website could not be fetched: "
                            f"{current_url}. "
                            f"{type(exc).__name__}: "
                            f"{exc}"
                        ) from exc

                    continue

                content_type = (
                    response.headers
                    .get(
                        "content-type",
                        "",
                    )
                    .lower()
                )

                if (
                    "text/html"
                    not in content_type
                ):
                    continue

                final_url = (
                    self._normalize_url(
                        str(
                            response.url
                        )
                    )
                )

                final_host = (
                    self._canonical_host(
                        final_url
                    )
                )

                if (
                    final_host
                    != base_host
                ):
                    continue

                if (
                    final_url
                    in discovered_urls
                ):
                    continue

                parser = (
                    WebsiteHTMLParser()
                )

                try:
                    parser.feed(
                        response.text
                    )

                except Exception:
                    continue

                text = (
                    parser.get_text()
                )

                if not self._is_usable_text(
                    text
                ):
                    continue

                title = (
                    parser.get_title()
                    or self._title_from_url(
                        final_url
                    )
                )

                normalized_content = (
                    self._build_document_text(
                        title=title,
                        url=final_url,
                        text=text,
                    )
                )

                content_bytes = (
                    normalized_content
                    .encode(
                        "utf-8"
                    )
                )

                checksum = (
                    hashlib.sha256(
                        content_bytes
                    )
                    .hexdigest()
                )

                item = SourceItem(
                    external_id=(
                        final_url
                    ),
                    title=title,
                    mime_type=(
                        "text/plain"
                    ),
                    checksum=checksum,
                    source_url=(
                        final_url
                    ),
                    filename=(
                        self._filename_for_url(
                            final_url
                        )
                    ),
                    metadata={
                        "source_type":
                            "WEBSITE",

                        "url":
                            final_url,

                        "http_status":
                            response
                            .status_code,
                    },
                    content=(
                        content_bytes
                    ),
                )

                items.append(
                    item
                )

                discovered_urls.add(
                    final_url
                )

                if depth >= max_depth:
                    continue

                for href in parser.links:

                    candidate = (
                        self._resolve_link(
                            current_url=(
                                final_url
                            ),
                            href=href,
                        )
                    )

                    if candidate is None:
                        continue

                    candidate_host = (
                        self._canonical_host(
                            candidate
                        )
                    )

                    if (
                        candidate_host
                        != base_host
                    ):
                        continue

                    if (
                        candidate
                        in visited_urls
                        or candidate
                        in queued_urls
                    ):
                        continue

                    if not self._should_include(
                        candidate,
                        include_patterns,
                        exclude_patterns,
                    ):
                        continue

                    queue.append(
                        (
                            candidate,
                            depth + 1,
                        )
                    )

                    queued_urls.add(
                        candidate
                    )

        return items

    def _resolve_link(
        self,
        current_url: str,
        href: str,
    ) -> str | None:

        href = href.strip()

        if not href:
            return None

        lowered = href.lower()

        if lowered.startswith(
            (
                "mailto:",
                "tel:",
                "javascript:",
                "data:",
            )
        ):
            return None

        absolute_url = urljoin(
            current_url,
            href,
        )

        return self._normalize_url(
            absolute_url
        )

    def _normalize_url(
        self,
        url: str,
    ) -> str:

        url = (
            url.strip()
        )

        if not url:
            raise ValueError(
                "Website URL cannot be empty."
            )

        parsed = urlparse(
            url
        )

        if not parsed.scheme:
            parsed = urlparse(
                f"https://{url}"
            )

        if (
            parsed.scheme
            not in {
                "http",
                "https",
            }
        ):
            raise ValueError(
                "Website URL must use "
                "http or https."
            )

        clean_url, _ = (
            urldefrag(
                urlunparse(
                    parsed
                )
            )
        )

        parsed = urlparse(
            clean_url
        )

        path = (
            parsed.path
            or "/"
        )

        if (
            path != "/"
            and path.endswith("/")
        ):
            path = path.rstrip(
                "/"
            )

        normalized = (
            parsed._replace(
                scheme=(
                    parsed.scheme.lower()
                ),
                netloc=(
                    parsed.netloc.lower()
                ),
                path=path,
                fragment="",
            )
        )

        return urlunparse(
            normalized
        )

    def _canonical_host(
        self,
        url: str,
    ) -> str:

        host = (
            urlparse(
                url
            )
            .netloc
            .lower()
        )

        if host.startswith(
            "www."
        ):
            host = host[4:]

        return host

    def _should_include(
        self,
        url: str,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ) -> bool:

        for pattern in exclude_patterns:
            if pattern in url:
                return False

        if not include_patterns:
            return True

        return any(
            pattern in url
            for pattern
            in include_patterns
        )

    def _is_usable_text(
        self,
        text: str,
    ) -> bool:

        if not text:
            return False

        alphanumeric_count = sum(
            character.isalnum()
            for character in text
        )

        return (
            alphanumeric_count
            >= 30
        )

    def _build_document_text(
        self,
        title: str,
        url: str,
        text: str,
    ) -> str:

        return (
            f"Title: {title}\n"
            f"Source URL: {url}\n\n"
            f"{text}\n"
        )

    def _title_from_url(
        self,
        url: str,
    ) -> str:

        parsed = urlparse(
            url
        )

        path = (
            parsed.path
            .strip("/")
        )

        if not path:
            return (
                parsed.netloc
            )

        last_part = (
            path
            .split("/")[-1]
        )

        title = (
            last_part
            .replace("-", " ")
            .replace("_", " ")
            .strip()
        )

        return (
            title.title()
            or parsed.netloc
        )

    def _filename_for_url(
        self,
        url: str,
    ) -> str:

        digest = (
            hashlib.sha256(
                url.encode(
                    "utf-8"
                )
            )
            .hexdigest()[:16]
        )

        return (
            f"website-{digest}.txt"
        )