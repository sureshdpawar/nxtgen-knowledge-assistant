"""
Read-only RAG retrieval debugger.

Usage:

    cd backend

    python scripts/debug_rag_chunks.py \
        --kb-id 0c905e3f-d1f6-4330-af76-dc581e33bb6c \
        --query "What is the mission of NXTGEN Innovate Technologies?" \
        --top-k 10

This script does NOT modify the database.
"""

import argparse
from uuid import UUID

from app.db.session import SessionLocal
from app.services.document_search_service import DocumentSearchService


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inspect Knowgentiq RAG retrieval results."
    )

    parser.add_argument(
        "--kb-id",
        required=True,
        help="Knowledge Base UUID.",
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Query to embed and search.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of retrieval candidates to inspect.",
    )

    return parser.parse_args()


def separator():
    print("\n" + "=" * 100)


def main():
    args = parse_args()

    knowledge_base_id = UUID(args.kb_id)

    db = SessionLocal()

    try:
        search_service = DocumentSearchService()

        results = search_service.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query=args.query,
            top_k_override=args.top_k,
        )

        separator()

        print("KNOWGENTIQ RAG RETRIEVAL DEBUG")

        print(f"KB:      {knowledge_base_id}")
        print(f"Query:   {args.query}")
        print(f"Top K:   {args.top_k}")
        print(f"Results: {len(results)}")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            (
                chunk,
                document,
                knowledge_source,
                distance,
            ) = result

            separator()

            text = chunk.text or ""

            print(f"RANK:        {rank}")
            print(f"DISTANCE:    {float(distance):.6f}")
            print(f"CHUNK ID:    {chunk.id}")
            print(f"CHUNK INDEX: {chunk.chunk_index}")
            print(f"CHARACTERS:  {len(text)}")

            print(
                "DOCUMENT ID:  "
                f"{document.id}"
            )

            print(
                "DOCUMENT:     "
                f"{document.original_filename}"
            )

            print(
                "EXTERNAL ID:  "
                f"{document.external_id}"
            )

            print(
                "SOURCE ID:    "
                f"{knowledge_source.id}"
            )

            print(
                "SOURCE:       "
                f"{knowledge_source.name}"
            )

            print("\nTEXT")
            print("-" * 100)

            print(text)

        separator()

    finally:
        db.close()


if __name__ == "__main__":
    main()