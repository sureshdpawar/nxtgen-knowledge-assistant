import pytest

from app.sources.website_url_canonicalizer import (
    WebsiteURLCanonicalizer,
)


@pytest.fixture
def canonicalizer():
    return WebsiteURLCanonicalizer()


def test_root_and_index_html_are_same_resource(
    canonicalizer,
):
    root = canonicalizer.canonicalize(
        "https://example.com/"
    )

    index = canonicalizer.canonicalize(
        "https://example.com/index.html"
    )

    assert root == "https://example.com/"
    assert index == root


def test_nested_index_html_collapses_to_directory(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com/docs/index.html"
    ) == "https://example.com/docs"


def test_trailing_slash_is_removed(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com/services/"
    ) == "https://example.com/services"


def test_fragment_is_removed(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com/services#ai"
    ) == "https://example.com/services"


def test_tracking_parameters_are_removed(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com/services"
        "?utm_source=google"
        "&fbclid=123"
        "&gclid=456"
    ) == "https://example.com/services"


def test_business_parameters_are_preserved(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com/products"
        "?category=ai"
        "&utm_source=linkedin"
        "&page=2"
    ) == (
        "https://example.com/products"
        "?category=ai&page=2"
    )


def test_query_order_does_not_change_identity(
    canonicalizer,
):
    first = canonicalizer.canonicalize(
        "https://example.com/search"
        "?q=rag&page=2"
    )

    second = canonicalizer.canonicalize(
        "https://example.com/search"
        "?page=2&q=rag"
    )

    assert first == second


def test_different_business_query_parameters_remain_distinct(
    canonicalizer,
):
    first = canonicalizer.canonicalize(
        "https://example.com/product?id=100"
    )

    second = canonicalizer.canonicalize(
        "https://example.com/product?id=200"
    )

    assert first != second


def test_default_ports_are_removed(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com:443/services"
    ) == "https://example.com/services"

    assert canonicalizer.canonicalize(
        "http://example.com:80/services"
    ) == "http://example.com/services"


def test_non_default_port_is_preserved(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "https://example.com:8443/services"
    ) == "https://example.com:8443/services"


def test_missing_scheme_defaults_to_https(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "example.com/services"
    ) == "https://example.com/services"


def test_relative_url_can_be_resolved(
    canonicalizer,
):
    assert canonicalizer.canonicalize(
        "../services/?utm_source=nav#ai",
        base_url=(
            "https://example.com/company/about"
        ),
    ) == "https://example.com/services"


def test_unsupported_scheme_is_rejected(
    canonicalizer,
):
    with pytest.raises(ValueError):
        canonicalizer.canonicalize(
            "ftp://example.com/file.txt"
        )
