# backend/scripts/debug_website_extraction.py

from __future__ import annotations

import argparse
from pathlib import Path

import httpx

from trafilatura import extract


USER_AGENT = (
    "Mozilla/5.0 "
    "(Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    with httpx.Client(
        follow_redirects=True,
        timeout=20.0,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    ) as client:
        response = client.get(url)
        response.raise_for_status()

        print(
            f"Fetched: {response.url} "
            f"status={response.status_code} "
            f"html_chars={len(response.text)}"
        )

        return response.text


def run_extraction(
    html: str,
    url: str,
    *,
    favor_precision: bool = False,
    favor_recall: bool = False,
) -> str:
    result = extract(
        html,
        url=url,
        output_format="markdown",
        include_comments=False,
        include_tables=True,
        include_links=False,
        favor_precision=favor_precision,
        favor_recall=favor_recall,
    )

    return (result or "").strip()


def print_result(
    name: str,
    text: str,
) -> None:
    print()
    print("=" * 100)
    print(name)
    print("=" * 100)
    print(f"characters={len(text)}")
    print()

    print(text)

    print()
    print("-" * 100)

    probes = [
        "Predictive Analytics",
        "Business Intelligence",
        "Generative AI",
        "RAG",
        "Agentic AI",
        "machine learning",
        "AI-powered automation",
    ]

    for probe in probes:
        found = probe.lower() in text.lower()

        print(
            f"{probe:<30} "
            f"{'FOUND' if found else 'MISSING'}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        required=True,
    )

    parser.add_argument(
        "--save-html",
        action="store_true",
    )

    args = parser.parse_args()

    html = fetch_html(args.url)

    if args.save_html:
        output = Path(
            "debug_ai_page.html"
        )

        output.write_text(
            html,
            encoding="utf-8",
        )

        print(
            f"Saved raw HTML to {output}"
        )

    variants = {
        "CURRENT: favor_precision=True":
            run_extraction(
                html,
                args.url,
                favor_precision=True,
            ),

        "DEFAULT":
            run_extraction(
                html,
                args.url,
            ),

        "RECALL: favor_recall=True":
            run_extraction(
                html,
                args.url,
                favor_recall=True,
            ),
    }

    for name, text in variants.items():
        print_result(
            name=name,
            text=text,
        )


if __name__ == "__main__":
    main()