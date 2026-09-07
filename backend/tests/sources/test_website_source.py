import httpx

from app.sources.website import WebsiteProvider


class SourceStub:
    def __init__(self, configuration):
        self.configuration = configuration


def html(title: str, body: str, links: str = "") -> str:
    return (
        "<html><head><title>"
        + title
        + "</title></head><body><main><h1>"
        + title
        + "</h1><p>"
        + body
        + "</p>"
        + links
        + "</main></body></html>"
    )


def response(url: str, text: str, content_type: str) -> httpx.Response:
    request = httpx.Request("GET", url)
    return httpx.Response(
        200,
        text=text,
        headers={"content-type": content_type},
        request=request,
    )


def test_parse_xml_urlset():
    provider = WebsiteProvider()
    xml = """<?xml version="1.0"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.com/a</loc></url>
      <url><loc>https://example.com/b</loc></url>
    </urlset>"""

    parsed = provider._parse_sitemap_response(
        response=response(
            "https://example.com/sitemap.xml",
            xml,
            "application/xml",
        ),
        sitemap_url="https://example.com/sitemap.xml",
    )

    assert parsed == (
        [],
        [
            "https://example.com/a",
            "https://example.com/b",
        ],
    )


def test_parse_xml_sitemap_index():
    provider = WebsiteProvider()
    xml = """<?xml version="1.0"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://example.com/pages.xml</loc></sitemap>
      <sitemap><loc>https://example.com/blog.xml</loc></sitemap>
    </sitemapindex>"""

    parsed = provider._parse_sitemap_response(
        response=response(
            "https://example.com/sitemap.xml",
            xml,
            "application/xml",
        ),
        sitemap_url="https://example.com/sitemap.xml",
    )

    assert parsed == (
        [
            "https://example.com/pages.xml",
            "https://example.com/blog.xml",
        ],
        [],
    )


def test_parse_html_sitemap():
    provider = WebsiteProvider()
    page = """
    <html><body>
      <a href="/courses">Courses</a>
      <a href="/about">About</a>
    </body></html>
    """

    parsed = provider._parse_sitemap_response(
        response=response(
            "https://example.com/sitemap",
            page,
            "text/html",
        ),
        sitemap_url="https://example.com/sitemap",
    )

    assert parsed == (
        [],
        [
            "https://example.com/courses",
            "https://example.com/about",
        ],
    )


def test_robots_supports_multiple_sitemaps():
    provider = WebsiteProvider()

    result = provider._parse_robots_sitemaps(
        """
        User-agent: *
        Sitemap: https://example.com/sitemap.xml
        sitemap: /products-sitemap.xml
        """,
        "https://example.com/robots.txt",
    )

    assert result == [
        "https://example.com/sitemap.xml",
        "https://example.com/products-sitemap.xml",
    ]


def test_structural_extraction_preserves_business_content():
    provider = WebsiteProvider()
    page = """
    <html><body>
      <nav>Home Services Contact</nav>
      <main>
        <h1>AI Solutions</h1>
        <h2>Generative AI</h2>
        <p>We build governed enterprise artificial intelligence systems.</p>
        <ul>
          <li>RAG (Retrieval Augmented Generation)</li>
          <li>Agentic AI</li>
        </ul>
      </main>
      <footer>Copyright Example Company</footer>
    </body></html>
    """

    text = provider._extract_structural_content(page)

    assert "Generative AI" in text
    assert "RAG (Retrieval Augmented Generation)" in text
    assert "Agentic AI" in text
    assert "Home Services Contact" not in text
    assert "Copyright Example Company" not in text


def test_merge_does_not_duplicate_existing_content():
    provider = WebsiteProvider()

    result = provider._merge_extractions(
        primary="""
        ## Generative AI

        We build Generative AI solutions.

        RAG (Retrieval Augmented Generation)
        """,
        supplemental="""
        ## Generative AI

        We build Generative AI solutions.

        - RAG (Retrieval Augmented Generation)

        - Agentic AI
        """,
    )

    assert result.casefold().count("generative ai solutions") == 1
    assert result.casefold().count(
        "rag (retrieval augmented generation)"
    ) == 1
    assert result.casefold().count("agentic ai") == 1



def test_placeholder_canonical_is_ignored():
    provider = WebsiteProvider()

    selected = provider._select_page_canonical_url(
        requested_url="https://example.com/courses",
        final_canonical_url="https://example.com/courses",
        declared_canonical_url="https://example.com/current-page-url",
        base_host="example.com",
    )

    assert selected == "https://example.com/courses"


def test_valid_same_site_canonical_is_honored():
    provider = WebsiteProvider()

    selected = provider._select_page_canonical_url(
        requested_url="https://example.com/course.php",
        final_canonical_url="https://example.com/course.php",
        declared_canonical_url="https://example.com/course",
        base_host="example.com",
    )

    assert selected == "https://example.com/course"


def test_common_sitemap_candidates_are_separate_fallback_groups():
    provider = WebsiteProvider()

    class Client:
        def get(self, url):
            request = httpx.Request("GET", url)
            return httpx.Response(
                404,
                text="not found",
                request=request,
            )

    groups = provider._sitemap_candidate_groups(
        client=Client(),
        configuration={},
        base_fetch_url="https://example.com/",
    )

    assert groups == [
        (
            "common:sitemap.xml",
            ["https://example.com/sitemap.xml"],
        ),
        (
            "common:sitemap_index.xml",
            ["https://example.com/sitemap_index.xml"],
        ),
        (
            "common:html-sitemap",
            ["https://example.com/sitemap"],
        ),
    ]



def test_page_outcome_reports_non_html():
    provider = WebsiteProvider()

    class Client:
        def get(self, url):
            request = httpx.Request("GET", url)
            return httpx.Response(
                200,
                content=b"%PDF",
                headers={"content-type": "application/pdf"},
                request=request,
            )

    outcome = provider._fetch_page_outcome(
        client=Client(),
        requested_url="https://example.com/brochure.pdf",
        base_host="example.com",
    )

    assert outcome.status == "non_html"
    assert outcome.item is None
    assert "application/pdf" in outcome.reason


def test_page_outcome_reports_out_of_scope_redirect():
    provider = WebsiteProvider()

    class Client:
        def get(self, url):
            original_request = httpx.Request("GET", url)
            redirect_response = httpx.Response(
                302,
                headers={
                    "location": "https://other.example/page",
                },
                request=original_request,
            )
            final_request = httpx.Request(
                "GET",
                "https://other.example/page",
            )
            return httpx.Response(
                200,
                text=(
                    "<html><body><p>"
                    "Enough useful text for a page."
                    "</p></body></html>"
                ),
                headers={"content-type": "text/html"},
                request=final_request,
                history=[redirect_response],
            )

    outcome = provider._fetch_page_outcome(
        client=Client(),
        requested_url="https://example.com/redirect",
        base_host="example.com",
    )

    assert outcome.status == "out_of_scope"
    assert outcome.item is None


def test_diagnostic_warning_is_bounded():
    provider = WebsiteProvider()
    warnings = []

    provider._append_diagnostic_warning(
        warnings,
        "Failures",
        [f"https://example.com/{i}" for i in range(12)],
        limit=3,
    )

    assert len(warnings) == 1
    assert "https://example.com/0" in warnings[0]
    assert "https://example.com/2" in warnings[0]
    assert "and 9 more" in warnings[0]
