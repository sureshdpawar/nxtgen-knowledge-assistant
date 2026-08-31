from __future__ import annotations

import hashlib
import logging
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

from bs4 import BeautifulSoup
from trafilatura import extract as trafilatura_extract

from app.models.knowledge_source import KnowledgeSource
from app.sources.base import KnowledgeSourceProvider
from app.sources.source_item import SourceItem
from app.sources.website_url_canonicalizer import (
    WebsiteURLCanonicalizer,
)


logger = logging.getLogger(__name__)


class WebsiteHTMLParser(HTMLParser):
    """
    Lightweight parser used for link discovery and title extraction.

    Content extraction is intentionally handled separately by
    WebsiteProvider because website content requires stronger
    boilerplate removal and structural preservation.
    """

    HARD_SKIPPED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
    }

    BOILERPLATE_TAGS = {
        "nav",
        "footer",
        "aside",
    }

    def __init__(self) -> None:
        super().__init__()

        self._hard_skip_depth = 0
        self._boilerplate_depth = 0

        self.links: list[str] = []
        self.title_parts: list[str] = []

        self._inside_title = False

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        tag = tag.lower()

        if tag in self.HARD_SKIPPED_TAGS:
            self._hard_skip_depth += 1
            return

        if tag in self.BOILERPLATE_TAGS:
            self._boilerplate_depth += 1

        if tag == "title":
            self._inside_title = True

        # Discover links even when they are inside nav/footer.
        # Navigation is often how the crawler discovers pages.
        if (
            tag == "a"
            and self._hard_skip_depth == 0
        ):
            href = dict(attrs).get("href")

            if href:
                self.links.append(href)

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = tag.lower()

        if tag in self.HARD_SKIPPED_TAGS:
            if self._hard_skip_depth > 0:
                self._hard_skip_depth -= 1

            return

        if tag in self.BOILERPLATE_TAGS:
            if self._boilerplate_depth > 0:
                self._boilerplate_depth -= 1

        if tag == "title":
            self._inside_title = False

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._hard_skip_depth > 0:
            return

        value = self._normalize_text(data)

        if not value:
            return

        if self._inside_title:
            self.title_parts.append(value)

    def get_title(self) -> str:
        return " ".join(
            self.title_parts
        ).strip()

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()


class WebsiteProvider(KnowledgeSourceProvider):
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

    STRUCTURAL_CONTENT_TAGS = (
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "li",
        "dt",
        "dd",
        "blockquote",
        "figcaption",
        "th",
        "td",
    )

    STRUCTURAL_PARENT_TAGS = {
        "ul",
        "ol",
        "dl",
        "table",
    }

    BOILERPLATE_TAGS = {
        "nav",
        "footer",
        "aside",
    }

    HARD_REMOVE_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
        "iframe",
    }

    URL_CANONICALIZER = WebsiteURLCanonicalizer()

    def discover(
        self,
        source: KnowledgeSource,
    ) -> list[SourceItem]:
        configuration = (
            source.configuration
            or {}
        )

        configured_base_url = (
            configuration.get("base_url")
            or configuration.get("url")
        )

        if not configured_base_url:
            raise ValueError(
                "Website source requires "
                "'base_url' in configuration."
            )

        base_fetch_url = self._normalize_url(
            configured_base_url
        )

        base_canonical_url = (
            self.URL_CANONICALIZER.canonicalize(
                base_fetch_url
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

        base_host = self._canonical_host(
            base_canonical_url
        )

        queue = deque(
            [
                (
                    base_fetch_url,
                    base_canonical_url,
                    0,
                )
            ]
        )

        queued_urls = {
            base_canonical_url
        }

        visited_urls: set[str] = set()
        discovered_urls: set[str] = set()

        items: list[SourceItem] = []

        with httpx.Client(
            follow_redirects=True,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
            headers={
                "User-Agent": self.USER_AGENT,
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
                and len(items) < max_pages
            ):
                (
                    current_fetch_url,
                    current_canonical_url,
                    depth,
                ) = queue.popleft()

                queued_urls.discard(
                    current_canonical_url
                )

                if (
                    current_canonical_url
                    in visited_urls
                ):
                    continue

                visited_urls.add(
                    current_canonical_url
                )

                if not self._should_include(
                    current_fetch_url,
                    include_patterns,
                    exclude_patterns,
                ):
                    continue

                try:
                    response = client.get(
                        current_fetch_url
                    )

                    response.raise_for_status()

                except httpx.HTTPStatusError as exc:
                    if depth == 0:
                        raise RuntimeError(
                            "Website could not be fetched. "
                            f"HTTP "
                            f"{exc.response.status_code} "
                            f"from {current_fetch_url}."
                        ) from exc

                    continue

                except httpx.HTTPError as exc:
                    if depth == 0:
                        raise RuntimeError(
                            "Website could not be fetched: "
                            f"{current_fetch_url}. "
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

                final_fetch_url = self._normalize_url(
                    str(response.url)
                )

                final_canonical_url = (
                    self.URL_CANONICALIZER
                    .canonicalize(
                        final_fetch_url
                    )
                )

                final_host = self._canonical_host(
                    final_canonical_url
                )

                if final_host != base_host:
                    continue

                #
                # A redirect can establish an identity different from
                # the originally queued URL. Mark the redirected identity
                # visited so a later discovered link does not fetch it
                # again.
                #
                visited_urls.add(
                    final_canonical_url
                )

                declared_canonical_url = (
                    self._extract_declared_canonical_url(
                        html_document=response.text,
                        base_url=final_fetch_url,
                    )
                )

                canonical_url = (
                    final_canonical_url
                )

                if declared_canonical_url:
                    declared_host = (
                        self._canonical_host(
                            declared_canonical_url
                        )
                    )

                    if declared_host == base_host:
                        canonical_url = (
                            declared_canonical_url
                        )
                    else:
                        logger.info(
                            "Ignoring cross-site HTML canonical "
                            "page=%s declared_canonical=%s",
                            final_fetch_url,
                            declared_canonical_url,
                        )

                visited_urls.add(
                    canonical_url
                )

                if (
                    canonical_url
                    in discovered_urls
                ):
                    logger.info(
                        "Skipping duplicate website resource "
                        "requested_url=%s fetched_url=%s "
                        "canonical_url=%s",
                        current_fetch_url,
                        final_fetch_url,
                        canonical_url,
                    )

                    continue

                parser = WebsiteHTMLParser()

                try:
                    parser.feed(
                        response.text
                    )
                except Exception:
                    logger.exception(
                        "Website HTML parsing failed "
                        "url=%s",
                        final_fetch_url,
                    )
                    continue

                title = (
                    parser.get_title()
                    or self._title_from_url(
                        canonical_url
                    )
                )

                (
                    text,
                    extraction_strategy,
                ) = self._extract_content(
                    html_document=response.text,
                    url=final_fetch_url,
                )

                if not self._is_usable_text(
                    text
                ):
                    continue

                normalized_content = (
                    self._build_document_text(
                        title=title,
                        text=text,
                    )
                )

                content_bytes = (
                    normalized_content.encode(
                        "utf-8"
                    )
                )

                checksum = (
                    hashlib.sha256(
                        content_bytes
                    )
                    .hexdigest()
                )

                logger.info(
                    "Website content extracted "
                    "requested_url=%s fetched_url=%s "
                    "canonical_url=%s strategy=%s "
                    "html_chars=%s content_chars=%s",
                    current_fetch_url,
                    final_fetch_url,
                    canonical_url,
                    extraction_strategy,
                    len(response.text),
                    len(normalized_content),
                )

                metadata = {
                    "source_type":
                        "WEBSITE",
                    "url":
                        canonical_url,
                    "canonical_url":
                        canonical_url,
                    "requested_url":
                        current_fetch_url,
                    "fetched_url":
                        final_fetch_url,
                    "http_status":
                        response.status_code,
                    "content_extraction":
                        extraction_strategy,
                }

                if declared_canonical_url:
                    metadata[
                        "declared_canonical_url"
                    ] = declared_canonical_url

                item = SourceItem(
                    external_id=canonical_url,
                    title=title,
                    mime_type="text/plain",
                    checksum=checksum,
                    source_url=final_fetch_url,
                    filename=(
                        self._filename_for_url(
                            canonical_url
                        )
                    ),
                    metadata=metadata,
                    content=content_bytes,
                )

                items.append(
                    item
                )

                discovered_urls.add(
                    canonical_url
                )

                if depth >= max_depth:
                    continue

                for href in parser.links:
                    candidate_fetch_url = (
                        self._resolve_link(
                            current_url=final_fetch_url,
                            href=href,
                        )
                    )

                    if candidate_fetch_url is None:
                        continue

                    try:
                        candidate_canonical_url = (
                            self.URL_CANONICALIZER
                            .canonicalize(
                                candidate_fetch_url
                            )
                        )
                    except ValueError:
                        continue

                    candidate_host = (
                        self._canonical_host(
                            candidate_canonical_url
                        )
                    )

                    if (
                        candidate_host
                        != base_host
                    ):
                        continue

                    if (
                        candidate_canonical_url
                        in visited_urls
                        or candidate_canonical_url
                        in queued_urls
                    ):
                        continue

                    if not self._should_include(
                        candidate_fetch_url,
                        include_patterns,
                        exclude_patterns,
                    ):
                        continue

                    queue.append(
                        (
                            candidate_fetch_url,
                            candidate_canonical_url,
                            depth + 1,
                        )
                    )

                    queued_urls.add(
                        candidate_canonical_url
                    )

        return items

    def _extract_content(
        self,
        html_document: str,
        url: str,
    ) -> tuple[str, str]:
        """
        Hybrid website extraction.

        Trafilatura provides high-quality main-content extraction.

        BeautifulSoup supplements semantic HTML content that may be
        represented as cards, tabs, accordions, feature grids, lists,
        or other application-style layouts that article-oriented
        extraction can omit.
        """

        trafilatura_text = (
            trafilatura_extract(
                html_document,
                url=url,
                output_format="markdown",
                include_comments=False,
                include_tables=True,
                include_links=False,
                favor_precision=True,
            )
            or ""
        )

        trafilatura_text = (
            self._normalize_document_text(
                trafilatura_text
            )
        )

        structural_text = (
            self._extract_structural_content(
                html_document
            )
        )

        if (
            trafilatura_text
            and structural_text
        ):
            merged = self._merge_extractions(
                primary=trafilatura_text,
                supplemental=structural_text,
            )

            return (
                merged,
                "trafilatura+structural-html-v1",
            )

        if trafilatura_text:
            return (
                trafilatura_text,
                "trafilatura-markdown-v1",
            )

        if structural_text:
            return (
                structural_text,
                "structural-html-v1",
            )

        return (
            "",
            "none",
        )

    def _extract_structural_content(
        self,
        html_document: str,
    ) -> str:
        """
        Extract semantic leaf-level content from the DOM.

        We deliberately do not extract generic div/span containers
        because nested layout elements create large amounts of
        duplicate text.

        The semantic tags below preserve content commonly found in:
        - headings
        - paragraphs
        - lists
        - cards
        - tabs
        - accordions
        - definition lists
        - tables
        """

        soup = BeautifulSoup(
            html_document,
            "html.parser",
        )

        for tag_name in self.HARD_REMOVE_TAGS:
            for tag in soup.find_all(
                tag_name
            ):
                tag.decompose()

        for tag_name in self.BOILERPLATE_TAGS:
            for tag in soup.find_all(
                tag_name
            ):
                tag.decompose()

        content_lines: list[str] = []

        seen_lines: set[str] = set()

        for element in soup.find_all(
            self.STRUCTURAL_CONTENT_TAGS
        ):
            # Avoid extracting a paragraph/list item again through
            # a nested semantic element.
            if element.find_parent(
                self.STRUCTURAL_CONTENT_TAGS
            ):
                continue

            text = element.get_text(
                " ",
                strip=True,
            )

            text = self._normalize_line(
                text
            )

            if not text:
                continue

            normalized_key = (
                self._dedupe_key(
                    text
                )
            )

            if not normalized_key:
                continue

            if normalized_key in seen_lines:
                continue

            seen_lines.add(
                normalized_key
            )

            prefix = (
                self._markdown_prefix(
                    element.name
                )
            )

            content_lines.append(
                f"{prefix}{text}"
            )

        return self._normalize_document_text(
            "\n\n".join(
                content_lines
            )
        )

    def _merge_extractions(
        self,
        primary: str,
        supplemental: str,
    ) -> str:
        """
        Merge main-content extraction with structural extraction.

        Exact normalized blocks already represented by Trafilatura
        are not appended again.

        Supplemental semantic blocks absent from the primary
        extraction are preserved.
        """

        primary = (
            self._normalize_document_text(
                primary
            )
        )

        supplemental = (
            self._normalize_document_text(
                supplemental
            )
        )

        if not primary:
            return supplemental

        if not supplemental:
            return primary

        primary_keys = {
            self._dedupe_key(block)
            for block
            in self._document_blocks(
                primary
            )
            if self._dedupe_key(
                block
            )
        }

        additional_blocks: list[str] = []

        seen_additional: set[str] = set()

        for block in self._document_blocks(
            supplemental
        ):
            key = self._dedupe_key(
                block
            )

            if not key:
                continue

            if key in primary_keys:
                continue

            if key in seen_additional:
                continue

            # Trafilatura may format the same text differently
            # from the structural extractor. Check normalized
            # containment before adding another copy.
            if self._block_exists_in_text(
                block=block,
                text=primary,
            ):
                continue

            seen_additional.add(
                key
            )

            additional_blocks.append(
                block
            )

        if not additional_blocks:
            return primary

        return self._normalize_document_text(
            primary
            + "\n\n"
            + "\n\n".join(
                additional_blocks
            )
        )

    def _block_exists_in_text(
        self,
        block: str,
        text: str,
    ) -> bool:
        block_key = self._dedupe_key(
            block
        )

        text_key = self._dedupe_key(
            text
        )

        if not block_key:
            return True

        return block_key in text_key

    def _document_blocks(
        self,
        text: str,
    ) -> list[str]:
        return [
            block.strip()
            for block
            in re.split(
                r"\n\s*\n",
                text,
            )
            if block.strip()
        ]

    def _markdown_prefix(
        self,
        tag_name: str,
    ) -> str:
        heading_prefixes = {
            "h1": "# ",
            "h2": "## ",
            "h3": "### ",
            "h4": "#### ",
            "h5": "##### ",
            "h6": "###### ",
        }

        if tag_name in heading_prefixes:
            return heading_prefixes[
                tag_name
            ]

        if tag_name in {
            "li",
            "dt",
            "dd",
        }:
            return "- "

        return ""

    def _normalize_line(
        self,
        text: str,
    ) -> str:
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _normalize_document_text(
        self,
        text: str,
    ) -> str:
        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r" *\n *",
            "\n",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def _dedupe_key(
        self,
        text: str,
    ) -> str:
        text = re.sub(
            r"^#{1,6}\s*",
            "",
            text.strip(),
        )

        text = re.sub(
            r"^[-*]\s*",
            "",
            text,
        )

        text = re.sub(
            r"[*_`]",
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip().casefold()

    def _extract_declared_canonical_url(
        self,
        html_document: str,
        base_url: str,
    ) -> str | None:
        """
        Read an HTML <link rel="canonical"> declaration.

        The caller is responsible for enforcing crawl-scope policy.
        This method only resolves and canonicalizes the declaration.
        """

        soup = BeautifulSoup(
            html_document,
            "html.parser",
        )

        for link in soup.find_all(
            "link",
            href=True,
        ):
            rel_value = (
                link.get("rel")
                or []
            )

            if isinstance(
                rel_value,
                str,
            ):
                rel_values = {
                    value.casefold()
                    for value
                    in rel_value.split()
                }
            else:
                rel_values = {
                    str(value).casefold()
                    for value
                    in rel_value
                }

            if (
                "canonical"
                not in rel_values
            ):
                continue

            href = str(
                link.get("href")
                or ""
            ).strip()

            if not href:
                continue

            try:
                return (
                    self.URL_CANONICALIZER
                    .canonicalize(
                        href,
                        base_url=base_url,
                    )
                )
            except ValueError:
                logger.info(
                    "Ignoring invalid HTML canonical "
                    "page=%s canonical=%s",
                    base_url,
                    href,
                )

                return None

        return None

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
        url = url.strip()

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

        clean_url, _ = urldefrag(
            urlunparse(
                parsed
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

        normalized = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=parsed.netloc.lower(),
            path=path,
            fragment="",
        )

        return urlunparse(
            normalized
        )

    def _canonical_host(
        self,
        url: str,
    ) -> str:
        host = (
            urlparse(url)
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
        text: str,
    ) -> str:
        """
        URL remains document metadata rather than embedding content.
        """

        title = self._normalize_line(
            title
        )

        text = self._normalize_document_text(
            text
        )

        if (
            title
            and not text.casefold().startswith(
                title.casefold()
            )
        ):
            return (
                f"# {title}\n\n"
                f"{text}\n"
            )

        return (
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
            return parsed.netloc

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