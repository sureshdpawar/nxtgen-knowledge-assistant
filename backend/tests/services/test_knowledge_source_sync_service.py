from app.sources.base import SourceDiscoveryResult


def test_authoritative_complete_result_allows_missing_reconciliation():
    result = SourceDiscoveryResult(
        items=[],
        strategy="sitemap",
        authoritative=True,
        complete=True,
        discovered_url_count=10,
    )

    assert result.allow_missing_reconciliation is True


def test_incomplete_sitemap_blocks_missing_reconciliation():
    result = SourceDiscoveryResult(
        items=[],
        strategy="sitemap",
        authoritative=True,
        complete=False,
        discovered_url_count=10,
        failed_url_count=1,
    )

    assert result.allow_missing_reconciliation is False


def test_html_crawl_blocks_missing_reconciliation():
    result = SourceDiscoveryResult(
        items=[],
        strategy="crawl",
        authoritative=False,
        complete=True,
        discovered_url_count=10,
    )

    assert result.allow_missing_reconciliation is False
