from __future__ import annotations

import hashlib
import logging
import re
import xml.etree.ElementTree as ET

from dataclasses import dataclass
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
from app.sources.base import (
    KnowledgeSourceProvider,
    SourceDiscoveryResult,
)
from app.sources.source_item import SourceItem
from app.sources.website_url_canonicalizer import WebsiteURLCanonicalizer


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WebsitePageFetchOutcome:
    requested_url: str
    status: str
    item: SourceItem | None = None
    canonical_url: str | None = None
    reason: str | None = None



class WebsiteHTMLParser(HTMLParser):
    """Lightweight parser for link discovery and title extraction."""

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

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()

        if tag in self.HARD_SKIPPED_TAGS:
            self._hard_skip_depth += 1
            return

        if tag in self.BOILERPLATE_TAGS:
            self._boilerplate_depth += 1

        if tag == "title":
            self._inside_title = True

        if tag == "a" and self._hard_skip_depth == 0:
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in self.HARD_SKIPPED_TAGS:
            if self._hard_skip_depth > 0:
                self._hard_skip_depth -= 1
            return

        if tag in self.BOILERPLATE_TAGS and self._boilerplate_depth > 0:
            self._boilerplate_depth -= 1

        if tag == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._hard_skip_depth > 0:
            return

        value = self._normalize_text(data)
        if value and self._inside_title:
            self.title_parts.append(value)

    def get_title(self) -> str:
        return " ".join(self.title_parts).strip()

    @staticmethod
    def _normalize_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


class WebsiteProvider(KnowledgeSourceProvider):
    """
    Generic website source provider.

    AUTO discovery order:
      1. configured sitemap URL(s)
      2. Sitemap declarations from robots.txt
      3. common sitemap locations
      4. existing bounded HTML crawl as a non-authoritative fallback

    Only a complete authoritative sitemap inventory permits missing-document
    reconciliation. A crawl fallback can add/update content but cannot prove
    that an unseen historical page was removed.
    """

    DEFAULT_MAX_PAGES = 500
    DEFAULT_MAX_DEPTH = 2
    DEFAULT_MAX_SITEMAPS = 50
    DEFAULT_TIMEOUT_SECONDS = 15.0

    DISCOVERY_MODE_AUTO = "auto"
    DISCOVERY_MODE_SITEMAP = "sitemap"
    DISCOVERY_MODE_CRAWL = "crawl"
    DISCOVERY_MODES = {
        DISCOVERY_MODE_AUTO,
        DISCOVERY_MODE_SITEMAP,
        DISCOVERY_MODE_CRAWL,
    }

    USER_AGENT = (
        "Mozilla/5.0 (compatible; KnowgentiqWebsiteCrawler/1.0; "
        "+https://nxtgeninnovate.com)"
    )

    STRUCTURAL_CONTENT_TAGS = (
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "li", "dt", "dd", "blockquote",
        "figcaption", "th", "td",
    )

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

    def discover(self, source: KnowledgeSource) -> list[SourceItem]:
        """Preserve the existing provider API."""
        return self.discover_result(source).items

    def discover_result(
        self,
        source: KnowledgeSource,
    ) -> SourceDiscoveryResult:
        configuration = source.configuration or {}
        base_fetch_url = self._configured_base_url(configuration)
        base_canonical_url = self.URL_CANONICALIZER.canonicalize(
            base_fetch_url
        )
        base_host = self._canonical_host(base_canonical_url)

        max_pages = self._positive_int(
            configuration.get("max_pages"),
            self.DEFAULT_MAX_PAGES,
            "max_pages",
        )
        max_depth = self._non_negative_int(
            configuration.get("max_depth"),
            self.DEFAULT_MAX_DEPTH,
            "max_depth",
        )
        max_sitemaps = self._positive_int(
            configuration.get("max_sitemaps"),
            self.DEFAULT_MAX_SITEMAPS,
            "max_sitemaps",
        )

        include_patterns = configuration.get("include_patterns", []) or []
        exclude_patterns = configuration.get("exclude_patterns", []) or []

        discovery_mode = str(
            configuration.get(
                "discovery_mode",
                self.DISCOVERY_MODE_AUTO,
            )
        ).strip().lower()

        if discovery_mode not in self.DISCOVERY_MODES:
            raise ValueError(
                "Website discovery_mode must be one of: "
                "auto, sitemap, crawl."
            )

        with self._client() as client:
            if discovery_mode != self.DISCOVERY_MODE_CRAWL:
                sitemap_result = self._discover_from_sitemaps(
                    client=client,
                    configuration=configuration,
                    base_fetch_url=base_fetch_url,
                    base_host=base_host,
                    max_pages=max_pages,
                    max_sitemaps=max_sitemaps,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                )

                if sitemap_result is not None:
                    return sitemap_result

                if discovery_mode == self.DISCOVERY_MODE_SITEMAP:
                    return SourceDiscoveryResult(
                        items=[],
                        strategy="sitemap",
                        authoritative=True,
                        complete=False,
                        discovered_url_count=0,
                        failed_url_count=0,
                        warnings=[
                            "No usable sitemap could be discovered. "
                            "Missing reconciliation was skipped."
                        ],
                    )

            return self._discover_by_crawl(
                client=client,
                base_fetch_url=base_fetch_url,
                base_canonical_url=base_canonical_url,
                base_host=base_host,
                max_pages=max_pages,
                max_depth=max_depth,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )

    def _discover_from_sitemaps(
        self,
        *,
        client: httpx.Client,
        configuration: dict,
        base_fetch_url: str,
        base_host: str,
        max_pages: int,
        max_sitemaps: int,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ) -> SourceDiscoveryResult | None:
        """
        Discover from the first usable sitemap source group.

        Priority is deliberate:
        1. explicitly configured sitemap URL(s)
        2. robots.txt Sitemap declarations
        3. common sitemap locations, tried one at a time

        We never union common fallback candidates. Once a usable sitemap
        source is found, lower-priority probes are irrelevant and cannot
        make that successful discovery incomplete.
        """
        groups = self._sitemap_candidate_groups(
            client=client,
            configuration=configuration,
            base_fetch_url=base_fetch_url,
        )

        for group_name, candidates in groups:
            if not candidates:
                continue

            result = self._discover_from_sitemap_group(
                client=client,
                sitemap_candidates=candidates,
                group_name=group_name,
                base_host=base_host,
                max_pages=max_pages,
                max_sitemaps=max_sitemaps,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )

            if result is not None:
                return result

        return None

    def _discover_from_sitemap_group(
        self,
        *,
        client: httpx.Client,
        sitemap_candidates: list[str],
        group_name: str,
        base_host: str,
        max_pages: int,
        max_sitemaps: int,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ) -> SourceDiscoveryResult | None:
        page_urls: list[str] = []
        seen_page_urls: set[str] = set()
        sitemap_queue = deque(sitemap_candidates)
        queued_sitemaps = set(sitemap_candidates)
        visited_sitemaps: set[str] = set()
        sitemap_failures = 0
        usable_sitemap_found = False
        warnings: list[str] = []

        while sitemap_queue and len(visited_sitemaps) < max_sitemaps:
            sitemap_url = sitemap_queue.popleft()
            queued_sitemaps.discard(sitemap_url)

            if sitemap_url in visited_sitemaps:
                continue

            visited_sitemaps.add(sitemap_url)

            try:
                response = client.get(sitemap_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                sitemap_failures += 1
                logger.info(
                    "Sitemap fetch failed group=%s url=%s error=%s",
                    group_name,
                    sitemap_url,
                    exc,
                )
                continue

            parsed = self._parse_sitemap_response(
                response=response,
                sitemap_url=sitemap_url,
            )

            if parsed is None:
                continue

            usable_sitemap_found = True
            child_sitemaps, discovered_pages = parsed

            for child in child_sitemaps:
                normalized = self._safe_normalize_url(
                    urljoin(str(response.url), child)
                )
                if normalized is None:
                    continue

                try:
                    child_canonical = self.URL_CANONICALIZER.canonicalize(
                        normalized
                    )
                except ValueError:
                    continue

                if self._canonical_host(child_canonical) != base_host:
                    continue

                if (
                    normalized in visited_sitemaps
                    or normalized in queued_sitemaps
                ):
                    continue

                sitemap_queue.append(normalized)
                queued_sitemaps.add(normalized)

            for page_url in discovered_pages:
                normalized = self._safe_normalize_url(
                    urljoin(str(response.url), page_url)
                )
                if normalized is None:
                    continue

                try:
                    canonical = self.URL_CANONICALIZER.canonicalize(
                        normalized
                    )
                except ValueError:
                    continue

                if self._canonical_host(canonical) != base_host:
                    continue

                if not self._should_include(
                    normalized,
                    include_patterns,
                    exclude_patterns,
                ):
                    continue

                if canonical in seen_page_urls:
                    continue

                seen_page_urls.add(canonical)
                page_urls.append(normalized)

        if not usable_sitemap_found:
            return None

        complete = True

        if sitemap_queue:
            complete = False
            warnings.append(
                f"Sitemap traversal reached max_sitemaps={max_sitemaps}."
            )

        # Failures inside the selected sitemap group matter. Failed probes in
        # lower-priority groups are never attempted and therefore cannot
        # degrade a successful inventory.
        if sitemap_failures:
            complete = False
            warnings.append(
                f"{sitemap_failures} selected sitemap fetch(es) failed."
            )

        discovered_url_count = len(page_urls)

        if len(page_urls) > max_pages:
            page_urls = page_urls[:max_pages]
            complete = False
            warnings.append(
                f"Sitemap contained {discovered_url_count} eligible URLs; "
                f"processing was limited to max_pages={max_pages}."
            )

        items: list[SourceItem] = []
        item_ids: set[str] = set()

        fetched_item_count = 0
        fetch_failure_count = 0
        non_html_count = 0
        unusable_count = 0
        out_of_scope_count = 0
        duplicate_count = 0

        duplicate_details: list[str] = []
        unusable_details: list[str] = []
        failure_details: list[str] = []
        out_of_scope_details: list[str] = []

        for page_url in page_urls:
            outcome = self._fetch_page_outcome(
                client=client,
                requested_url=page_url,
                base_host=base_host,
            )

            if outcome.status == "failed":
                fetch_failure_count += 1
                failure_details.append(
                    self._diagnostic_entry(
                        outcome.requested_url,
                        outcome.reason,
                    )
                )
                continue

            if outcome.status == "non_html":
                non_html_count += 1
                unusable_details.append(
                    self._diagnostic_entry(
                        outcome.requested_url,
                        outcome.reason,
                    )
                )
                continue

            if outcome.status == "unusable":
                unusable_count += 1
                unusable_details.append(
                    self._diagnostic_entry(
                        outcome.requested_url,
                        outcome.reason,
                    )
                )
                continue

            if outcome.status == "out_of_scope":
                out_of_scope_count += 1
                out_of_scope_details.append(
                    self._diagnostic_entry(
                        outcome.requested_url,
                        outcome.reason,
                    )
                )
                continue

            item = outcome.item
            if item is None:
                fetch_failure_count += 1
                failure_details.append(
                    self._diagnostic_entry(
                        outcome.requested_url,
                        "unexpected empty page outcome",
                    )
                )
                continue

            fetched_item_count += 1

            if item.external_id in item_ids:
                duplicate_count += 1
                duplicate_details.append(
                    (
                        f"{outcome.requested_url} -> "
                        f"{item.external_id}"
                    )
                )
                continue

            item_ids.add(item.external_id)
            items.append(item)

        accounted_count = (
            len(items)
            + duplicate_count
            + fetch_failure_count
            + non_html_count
            + unusable_count
            + out_of_scope_count
        )

        if accounted_count != len(page_urls):
            complete = False
            warnings.append(
                "Internal sitemap accounting mismatch: "
                f"selected={len(page_urls)}, accounted={accounted_count}."
            )

        if (
            fetch_failure_count
            or non_html_count
            or unusable_count
            or out_of_scope_count
            or duplicate_count
        ):
            complete = False

        warnings.append(
            "Sitemap accounting: "
            f"inventory={discovered_url_count}; "
            f"selected={len(page_urls)}; "
            f"fetched_items={fetched_item_count}; "
            f"unique_items={len(items)}; "
            f"duplicates={duplicate_count}; "
            f"fetch_failures={fetch_failure_count}; "
            f"non_html={non_html_count}; "
            f"unusable={unusable_count}; "
            f"out_of_scope={out_of_scope_count}."
        )

        self._append_diagnostic_warning(
            warnings,
            "Duplicate/canonical-collapsed URLs",
            duplicate_details,
        )
        self._append_diagnostic_warning(
            warnings,
            "Unusable/non-HTML URLs",
            unusable_details,
        )
        self._append_diagnostic_warning(
            warnings,
            "Fetch failures",
            failure_details,
        )
        self._append_diagnostic_warning(
            warnings,
            "Redirected out-of-scope URLs",
            out_of_scope_details,
        )

        return SourceDiscoveryResult(
            items=items,
            strategy=f"sitemap:{group_name}",
            authoritative=True,
            complete=complete,
            discovered_url_count=discovered_url_count,
            failed_url_count=(
                fetch_failure_count
                + sitemap_failures
            ),
            warnings=warnings,
        )

    def _sitemap_candidate_groups(
        self,
        *,
        client: httpx.Client,
        configuration: dict,
        base_fetch_url: str,
    ) -> list[tuple[str, list[str]]]:
        configured = configuration.get("sitemap_urls")
        if configured is None:
            configured = configuration.get("sitemap_url")

        if isinstance(configured, str):
            configured_values = [configured]
        elif isinstance(configured, (list, tuple)):
            configured_values = list(configured)
        else:
            configured_values = []

        configured_candidates = self._normalize_unique_urls(
            [
                urljoin(base_fetch_url, str(value).strip())
                for value in configured_values
                if str(value).strip()
            ]
        )

        robots_candidates: list[str] = []
        robots_url = urljoin(base_fetch_url, "/robots.txt")

        try:
            response = client.get(robots_url)
            if response.is_success:
                robots_candidates = self._normalize_unique_urls(
                    self._parse_robots_sitemaps(
                        response.text,
                        robots_url,
                    )
                )
        except httpx.HTTPError:
            logger.info(
                "robots.txt could not be fetched url=%s",
                robots_url,
            )

        # Common candidates are separate fallback groups. This prevents a
        # valid /sitemap.xml from being combined with /sitemap HTML or being
        # degraded by a missing /sitemap_index.xml.
        groups: list[tuple[str, list[str]]] = []

        if configured_candidates:
            groups.append(("configured", configured_candidates))

        if robots_candidates:
            groups.append(("robots", robots_candidates))

        groups.extend(
            [
                (
                    "common:sitemap.xml",
                    self._normalize_unique_urls(
                        [urljoin(base_fetch_url, "/sitemap.xml")]
                    ),
                ),
                (
                    "common:sitemap_index.xml",
                    self._normalize_unique_urls(
                        [urljoin(base_fetch_url, "/sitemap_index.xml")]
                    ),
                ),
                (
                    "common:html-sitemap",
                    self._normalize_unique_urls(
                        [urljoin(base_fetch_url, "/sitemap")]
                    ),
                ),
            ]
        )

        return groups

    def _normalize_unique_urls(
        self,
        urls: list[str],
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for url in urls:
            normalized = self._safe_normalize_url(url)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)

        return result

    def _parse_robots_sitemaps(
        self,
        robots_text: str,
        robots_url: str,
    ) -> list[str]:
        result: list[str] = []

        for raw_line in robots_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            key, separator, value = line.partition(":")
            if not separator or key.strip().casefold() != "sitemap":
                continue

            value = value.strip()
            if value:
                result.append(urljoin(robots_url, value))

        return result

    def _parse_sitemap_response(
        self,
        *,
        response: httpx.Response,
        sitemap_url: str,
    ) -> tuple[list[str], list[str]] | None:
        text = response.text
        stripped = text.lstrip()
        content_type = response.headers.get("content-type", "").lower()

        looks_xml = (
            "xml" in content_type
            or stripped.startswith("<?xml")
            or stripped.startswith("<urlset")
            or stripped.startswith("<sitemapindex")
        )

        if looks_xml:
            try:
                root = ET.fromstring(text)
            except ET.ParseError:
                logger.info(
                    "Invalid XML sitemap url=%s",
                    sitemap_url,
                )
                return None

            root_name = self._xml_local_name(root.tag)

            if root_name == "urlset":
                pages = [
                    (loc.text or "").strip()
                    for loc in root.iter()
                    if self._xml_local_name(loc.tag) == "loc"
                    and (loc.text or "").strip()
                ]
                return [], pages

            if root_name == "sitemapindex":
                children = [
                    (loc.text or "").strip()
                    for loc in root.iter()
                    if self._xml_local_name(loc.tag) == "loc"
                    and (loc.text or "").strip()
                ]
                return children, []

            return None

        looks_html = (
            "text/html" in content_type
            or "<html" in stripped[:500].casefold()
            or "<a " in text.casefold()
        )

        if not looks_html:
            return None

        parser = WebsiteHTMLParser()
        try:
            parser.feed(text)
        except Exception:
            logger.exception(
                "HTML sitemap parsing failed url=%s",
                sitemap_url,
            )
            return None

        pages = [
            urljoin(str(response.url), href)
            for href in parser.links
        ]

        if not pages:
            return None

        return [], pages

    def _discover_by_crawl(
        self,
        *,
        client: httpx.Client,
        base_fetch_url: str,
        base_canonical_url: str,
        base_host: str,
        max_pages: int,
        max_depth: int,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ) -> SourceDiscoveryResult:
        queue = deque(
            [(base_fetch_url, base_canonical_url, 0)]
        )
        queued_urls = {base_canonical_url}
        visited_urls: set[str] = set()
        item_ids: set[str] = set()
        items: list[SourceItem] = []
        failed_url_count = 0
        truncated = False

        while queue:
            if len(items) >= max_pages:
                truncated = True
                break

            current_fetch_url, current_canonical_url, depth = queue.popleft()
            queued_urls.discard(current_canonical_url)

            if current_canonical_url in visited_urls:
                continue

            visited_urls.add(current_canonical_url)

            if not self._should_include(
                current_fetch_url,
                include_patterns,
                exclude_patterns,
            ):
                continue

            try:
                response = client.get(current_fetch_url)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if depth == 0:
                    raise RuntimeError(
                        "Website could not be fetched. "
                        f"HTTP {exc.response.status_code} "
                        f"from {current_fetch_url}."
                    ) from exc
                failed_url_count += 1
                continue
            except httpx.HTTPError as exc:
                if depth == 0:
                    raise RuntimeError(
                        "Website could not be fetched: "
                        f"{current_fetch_url}. "
                        f"{type(exc).__name__}: {exc}"
                    ) from exc
                failed_url_count += 1
                continue

            item, parser, canonical_url = self._page_item_from_response(
                requested_url=current_fetch_url,
                response=response,
                base_host=base_host,
            )

            if canonical_url:
                visited_urls.add(canonical_url)

            if item is not None and item.external_id not in item_ids:
                item_ids.add(item.external_id)
                items.append(item)

            if parser is None or depth >= max_depth:
                continue

            final_fetch_url = self._normalize_url(str(response.url))

            for href in parser.links:
                candidate_fetch_url = self._resolve_link(
                    current_url=final_fetch_url,
                    href=href,
                )
                if candidate_fetch_url is None:
                    continue

                try:
                    candidate_canonical_url = (
                        self.URL_CANONICALIZER.canonicalize(
                            candidate_fetch_url
                        )
                    )
                except ValueError:
                    continue

                if self._canonical_host(candidate_canonical_url) != base_host:
                    continue

                if (
                    candidate_canonical_url in visited_urls
                    or candidate_canonical_url in queued_urls
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
                queued_urls.add(candidate_canonical_url)

        warnings = [
            "HTML crawl discovery is non-authoritative; "
            "missing reconciliation was skipped."
        ]

        if truncated:
            warnings.append(
                f"HTML crawl reached max_pages={max_pages}."
            )

        if failed_url_count:
            warnings.append(
                f"{failed_url_count} crawled page(s) failed."
            )

        return SourceDiscoveryResult(
            items=items,
            strategy="crawl",
            authoritative=False,
            complete=not truncated and failed_url_count == 0,
            discovered_url_count=len(visited_urls),
            failed_url_count=failed_url_count,
            warnings=warnings,
        )

    def _fetch_page_item(
        self,
        *,
        client: httpx.Client,
        requested_url: str,
        base_host: str,
    ) -> SourceItem | None:
        """Compatibility wrapper used by callers that only need the item."""
        return self._fetch_page_outcome(
            client=client,
            requested_url=requested_url,
            base_host=base_host,
        ).item

    def _fetch_page_outcome(
        self,
        *,
        client: httpx.Client,
        requested_url: str,
        base_host: str,
    ) -> WebsitePageFetchOutcome:
        try:
            response = client.get(requested_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="failed",
                reason=f"HTTP {exc.response.status_code}",
            )
        except httpx.HTTPError as exc:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="failed",
                reason=f"{type(exc).__name__}: {exc}",
            )

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "text/html" not in content_type:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="non_html",
                reason=(
                    f"content-type={content_type or 'missing'}; "
                    f"fetched_url={response.url}"
                ),
            )

        final_fetch_url = self._normalize_url(
            str(response.url)
        )

        try:
            final_canonical_url = (
                self.URL_CANONICALIZER.canonicalize(
                    final_fetch_url
                )
            )
        except ValueError as exc:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="failed",
                reason=f"invalid final URL: {exc}",
            )

        if self._canonical_host(final_canonical_url) != base_host:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="out_of_scope",
                canonical_url=final_canonical_url,
                reason=(
                    f"redirected to {final_fetch_url}"
                ),
            )

        item, _, canonical_url = self._page_item_from_response(
            requested_url=requested_url,
            response=response,
            base_host=base_host,
        )

        if item is None:
            return WebsitePageFetchOutcome(
                requested_url=requested_url,
                status="unusable",
                canonical_url=canonical_url,
                reason=(
                    "HTML fetched successfully but did not contain "
                    "enough usable extractable text"
                ),
            )

        return WebsitePageFetchOutcome(
            requested_url=requested_url,
            status="item",
            item=item,
            canonical_url=item.external_id,
        )

    def _page_item_from_response(
        self,
        *,
        requested_url: str,
        response: httpx.Response,
        base_host: str,
    ) -> tuple[SourceItem | None, WebsiteHTMLParser | None, str | None]:
        content_type = response.headers.get("content-type", "").lower()

        if "text/html" not in content_type:
            return None, None, None

        final_fetch_url = self._normalize_url(str(response.url))
        final_canonical_url = self.URL_CANONICALIZER.canonicalize(
            final_fetch_url
        )

        if self._canonical_host(final_canonical_url) != base_host:
            return None, None, final_canonical_url

        declared_canonical_url = self._extract_declared_canonical_url(
            html_document=response.text,
            base_url=final_fetch_url,
        )

        canonical_url = self._select_page_canonical_url(
            requested_url=requested_url,
            final_canonical_url=final_canonical_url,
            declared_canonical_url=declared_canonical_url,
            base_host=base_host,
        )

        parser = WebsiteHTMLParser()

        try:
            parser.feed(response.text)
        except Exception:
            logger.exception(
                "Website HTML parsing failed url=%s",
                final_fetch_url,
            )
            return None, None, canonical_url

        title = parser.get_title() or self._title_from_url(canonical_url)

        text, extraction_strategy = self._extract_content(
            html_document=response.text,
            url=final_fetch_url,
        )

        if not self._is_usable_text(text):
            return None, parser, canonical_url

        normalized_content = self._build_document_text(
            title=title,
            text=text,
        )
        content_bytes = normalized_content.encode("utf-8")
        checksum = hashlib.sha256(content_bytes).hexdigest()

        metadata = {
            "source_type": "WEBSITE",
            "url": canonical_url,
            "canonical_url": canonical_url,
            "requested_url": requested_url,
            "fetched_url": final_fetch_url,
            "http_status": response.status_code,
            "content_extraction": extraction_strategy,
        }

        if declared_canonical_url:
            metadata["declared_canonical_url"] = declared_canonical_url

        logger.info(
            "Website content extracted requested_url=%s fetched_url=%s "
            "canonical_url=%s strategy=%s html_chars=%s content_chars=%s",
            requested_url,
            final_fetch_url,
            canonical_url,
            extraction_strategy,
            len(response.text),
            len(normalized_content),
        )

        return (
            SourceItem(
                external_id=canonical_url,
                title=title,
                mime_type="text/plain",
                checksum=checksum,
                source_url=final_fetch_url,
                filename=self._filename_for_url(canonical_url),
                metadata=metadata,
                content=content_bytes,
            ),
            parser,
            canonical_url,
        )

    def _select_page_canonical_url(
        self,
        *,
        requested_url: str,
        final_canonical_url: str,
        declared_canonical_url: str | None,
        base_host: str,
    ) -> str:
        """
        Select a safe document identity.

        Same-site canonical declarations are normally honored. However, a
        generic crawler must defend against template placeholders and other
        obviously non-page canonicals that would collapse unrelated sitemap
        URLs into one document.

        We intentionally keep this rule generic and conservative rather than
        encoding customer-specific paths.
        """
        if not declared_canonical_url:
            return final_canonical_url

        if self._canonical_host(declared_canonical_url) != base_host:
            logger.info(
                "Ignoring cross-site HTML canonical "
                "page=%s declared_canonical=%s",
                requested_url,
                declared_canonical_url,
            )
            return final_canonical_url

        if self._looks_like_placeholder_canonical(
            declared_canonical_url
        ):
            logger.warning(
                "Ignoring placeholder-like HTML canonical "
                "page=%s declared_canonical=%s",
                requested_url,
                declared_canonical_url,
            )
            return final_canonical_url

        return declared_canonical_url

    def _looks_like_placeholder_canonical(
        self,
        canonical_url: str,
    ) -> bool:
        path = urlparse(canonical_url).path.casefold().strip("/")

        if not path:
            return False

        normalized = re.sub(r"[-_]+", " ", path)
        placeholder_tokens = {
            "current page url",
            "current page",
            "page url",
            "your page url",
            "canonical url",
            "example page",
            "placeholder",
        }

        return normalized in placeholder_tokens

    def _extract_content(
        self,
        html_document: str,
        url: str,
    ) -> tuple[str, str]:
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

        trafilatura_text = self._normalize_document_text(
            trafilatura_text
        )
        structural_text = self._extract_structural_content(
            html_document
        )

        if trafilatura_text and structural_text:
            return (
                self._merge_extractions(
                    primary=trafilatura_text,
                    supplemental=structural_text,
                ),
                "trafilatura+structural-html-v1",
            )

        if trafilatura_text:
            return trafilatura_text, "trafilatura-markdown-v1"

        if structural_text:
            return structural_text, "structural-html-v1"

        return "", "none"

    def _extract_structural_content(
        self,
        html_document: str,
    ) -> str:
        soup = BeautifulSoup(html_document, "html.parser")

        for tag_name in self.HARD_REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        for tag_name in self.BOILERPLATE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        content_lines: list[str] = []
        seen_lines: set[str] = set()

        for element in soup.find_all(self.STRUCTURAL_CONTENT_TAGS):
            if element.find_parent(self.STRUCTURAL_CONTENT_TAGS):
                continue

            text = self._normalize_line(
                element.get_text(" ", strip=True)
            )
            if not text:
                continue

            normalized_key = self._dedupe_key(text)
            if not normalized_key or normalized_key in seen_lines:
                continue

            seen_lines.add(normalized_key)
            prefix = self._markdown_prefix(element.name)
            content_lines.append(f"{prefix}{text}")

        return self._normalize_document_text(
            "\n\n".join(content_lines)
        )

    def _merge_extractions(
        self,
        primary: str,
        supplemental: str,
    ) -> str:
        primary = self._normalize_document_text(primary)
        supplemental = self._normalize_document_text(supplemental)

        if not primary:
            return supplemental
        if not supplemental:
            return primary

        primary_keys = {
            self._dedupe_key(block)
            for block in self._document_blocks(primary)
            if self._dedupe_key(block)
        }

        additional_blocks: list[str] = []
        seen_additional: set[str] = set()

        for block in self._document_blocks(supplemental):
            key = self._dedupe_key(block)

            if not key:
                continue
            if key in primary_keys or key in seen_additional:
                continue
            if self._block_exists_in_text(block=block, text=primary):
                continue

            seen_additional.add(key)
            additional_blocks.append(block)

        if not additional_blocks:
            return primary

        return self._normalize_document_text(
            primary + "\n\n" + "\n\n".join(additional_blocks)
        )

    def _block_exists_in_text(self, block: str, text: str) -> bool:
        block_key = self._dedupe_key(block)
        text_key = self._dedupe_key(text)
        if not block_key:
            return True
        return block_key in text_key

    def _document_blocks(self, text: str) -> list[str]:
        return [
            block.strip()
            for block in re.split(r"\n\s*\n", text)
            if block.strip()
        ]

    def _markdown_prefix(self, tag_name: str) -> str:
        heading_prefixes = {
            "h1": "# ",
            "h2": "## ",
            "h3": "### ",
            "h4": "#### ",
            "h5": "##### ",
            "h6": "###### ",
        }

        if tag_name in heading_prefixes:
            return heading_prefixes[tag_name]

        if tag_name in {"li", "dt", "dd"}:
            return "- "

        return ""

    def _normalize_line(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _normalize_document_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _dedupe_key(self, text: str) -> str:
        text = re.sub(r"^#{1,6}\s*", "", text.strip())
        text = re.sub(r"^[-*]\s*", "", text)
        text = re.sub(r"[*_`]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip().casefold()

    def _extract_declared_canonical_url(
        self,
        html_document: str,
        base_url: str,
    ) -> str | None:
        soup = BeautifulSoup(html_document, "html.parser")

        for link in soup.find_all("link", href=True):
            rel_value = link.get("rel") or []

            if isinstance(rel_value, str):
                rel_values = {
                    value.casefold()
                    for value in rel_value.split()
                }
            else:
                rel_values = {
                    str(value).casefold()
                    for value in rel_value
                }

            if "canonical" not in rel_values:
                continue

            href = str(link.get("href") or "").strip()
            if not href:
                continue

            try:
                return self.URL_CANONICALIZER.canonicalize(
                    href,
                    base_url=base_url,
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
            ("mailto:", "tel:", "javascript:", "data:")
        ):
            return None

        return self._normalize_url(urljoin(current_url, href))

    def _configured_base_url(self, configuration: dict) -> str:
        configured = (
            configuration.get("base_url")
            or configuration.get("url")
        )

        if not configured:
            raise ValueError(
                "Website source requires 'base_url' in configuration."
            )

        return self._normalize_url(str(configured))

    def _normalize_url(self, url: str) -> str:
        url = url.strip()

        if not url:
            raise ValueError("Website URL cannot be empty.")

        parsed = urlparse(url)

        if not parsed.scheme:
            parsed = urlparse(f"https://{url}")

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Website URL must use http or https."
            )

        clean_url, _ = urldefrag(urlunparse(parsed))
        parsed = urlparse(clean_url)
        path = parsed.path or "/"

        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        normalized = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=parsed.netloc.lower(),
            path=path,
            fragment="",
        )

        return urlunparse(normalized)

    def _safe_normalize_url(self, url: str) -> str | None:
        try:
            return self._normalize_url(url)
        except ValueError:
            return None

    def _canonical_host(self, url: str) -> str:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
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
            for pattern in include_patterns
        )

    def _is_usable_text(self, text: str) -> bool:
        if not text:
            return False

        alphanumeric_count = sum(
            character.isalnum()
            for character in text
        )
        return alphanumeric_count >= 30

    def _build_document_text(
        self,
        title: str,
        text: str,
    ) -> str:
        title = self._normalize_line(title)
        text = self._normalize_document_text(text)

        if title and not text.casefold().startswith(
            title.casefold()
        ):
            return f"# {title}\n\n{text}\n"

        return f"{text}\n"

    def _title_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if not path:
            return parsed.netloc

        last_part = path.split("/")[-1]
        title = (
            last_part
            .replace("-", " ")
            .replace("_", " ")
            .strip()
        )
        return title.title() or parsed.netloc

    def _filename_for_url(self, url: str) -> str:
        digest = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()[:16]
        return f"website-{digest}.txt"

    def _diagnostic_entry(
        self,
        url: str,
        reason: str | None,
    ) -> str:
        if reason:
            return f"{url} ({reason})"
        return url

    def _append_diagnostic_warning(
        self,
        warnings: list[str],
        label: str,
        entries: list[str],
        limit: int = 10,
    ) -> None:
        if not entries:
            return

        visible = entries[:limit]
        suffix = ""

        if len(entries) > limit:
            suffix = (
                f" ... and {len(entries) - limit} more"
            )

        warnings.append(
            f"{label}: "
            + "; ".join(visible)
            + suffix
        )

    def _client(self) -> httpx.Client:
        return httpx.Client(
            follow_redirects=True,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml,text/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )

    @staticmethod
    def _xml_local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1].casefold()

    @staticmethod
    def _positive_int(
        value,
        default: int,
        field_name: str,
    ) -> int:
        result = default if value is None else int(value)
        if result <= 0:
            raise ValueError(f"{field_name} must be greater than zero.")
        return result

    @staticmethod
    def _non_negative_int(
        value,
        default: int,
        field_name: str,
    ) -> int:
        result = default if value is None else int(value)
        if result < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return result
