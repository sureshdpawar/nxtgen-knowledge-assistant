import pytest

from app.services.document_chunking_service import (
    DocumentChunkingService,
)


def test_chunk_preserves_natural_text_boundaries():
    service = (
        DocumentChunkingService()
    )

    pages = [
        {
            "page": 1,
            "text": """
# Our Mission

NXTGEN Innovate Technologies empowers organizations with
technology, innovation, and talent so they can adapt,
innovate, and thrive in a fast-changing digital world.

# Our Services

NXTGEN Innovate Technologies provides software development,
AI solutions, consulting, cloud services, and staffing
services for organizations.
""".strip(),
        }
    ]

    chunks = service.chunk(
        pages=pages,
        chunk_size=180,
        chunk_overlap=30,
    )

    assert chunks

    assert all(
        chunk["text"]
        for chunk in chunks
    )

    assert all(
        chunk["text"]
        == chunk["text"].strip()
        for chunk in chunks
    )

    assert all(
        chunk["page"] == 1
        for chunk in chunks
    )

    assert all(
        len(
            chunk["text"]
        )
        <= 180
        for chunk in chunks
    )

    combined_text = "\n".join(
        chunk["text"]
        for chunk in chunks
    )

    assert (
        "Our Mission"
        in combined_text
    )

    assert (
        "empowers organizations"
        in combined_text
    )

    assert (
        "Our Services"
        in combined_text
    )

    #
    # These are representative examples
    # of the pathological fragments
    # produced by the previous raw
    # character slicing implementation.
    #
    assert "\ninn\n" not in (
        combined_text
    )

    assert "\nact Us\n" not in (
        combined_text
    )


def test_chunk_skips_empty_pages():
    service = (
        DocumentChunkingService()
    )

    chunks = service.chunk(
        pages=[
            {
                "page": 1,
                "text": "",
            },
            {
                "page": 2,
                "text": "   \n\n   ",
            },
            {
                "page": 3,
                "text": (
                    "Meaningful content "
                    "for retrieval."
                ),
            },
        ],
        chunk_size=100,
        chunk_overlap=10,
    )

    assert len(
        chunks
    ) == 1

    assert (
        chunks[0]["page"]
        == 3
    )


@pytest.mark.parametrize(
    (
        "chunk_size",
        "chunk_overlap",
    ),
    [
        (
            0,
            0,
        ),
        (
            -1,
            0,
        ),
        (
            100,
            -1,
        ),
        (
            100,
            100,
        ),
        (
            100,
            101,
        ),
    ],
)
def test_chunk_rejects_invalid_configuration(
    chunk_size,
    chunk_overlap,
):
    service = (
        DocumentChunkingService()
    )

    with pytest.raises(
        ValueError
    ):
        service.chunk(
            pages=[
                {
                    "page": 1,
                    "text": (
                        "Some content."
                    ),
                }
            ],
            chunk_size=(
                chunk_size
            ),
            chunk_overlap=(
                chunk_overlap
            ),
        )


def test_chunk_reports_strategy_name():
    service = (
        DocumentChunkingService()
    )

    assert (
        service.strategy_name
        == "recursive-character-v1"
    )