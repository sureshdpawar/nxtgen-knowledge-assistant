import argparse
from uuid import UUID

from app.db.session import SessionLocal
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.services.document_search_service import (
    DocumentSearchService,
)
from app.services.reranker_service import (
    RerankerService,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Debug Knowgentiq two-stage "
            "RAG retrieval and reranking."
        )
    )

    parser.add_argument(
        "--kb-id",
        required=True,
        help="Knowledge Base UUID",
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Search query",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help=(
            "Final number of chunks after "
            "reranking."
        ),
    )

    parser.add_argument(
        "--candidate-k",
        type=int,
        default=None,
        help=(
            "Optional candidate pool size. "
            "Defaults to the same expansion "
            "policy used by "
            "DocumentSearchService."
        ),
    )

    parser.add_argument(
        "--reranker-model",
        default=None,
        help=(
            "Optional Hugging Face "
            "CrossEncoder reranker model. "
            "If omitted, the default "
            "RerankerService model is used."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_args()

    knowledge_base_id = UUID(
        args.kb_id
    )

    if args.top_k < 1:
        raise ValueError(
            "--top-k must be greater than 0."
        )

    service = DocumentSearchService()

    #
    # Diagnostic-only model override.
    #
    # Production behavior is unchanged.
    #
    if args.reranker_model:
        service.reranker_service = (
            RerankerService(
                model_name=
                    args.reranker_model,
            )
        )

    candidate_top_k = (
        args.candidate_k
        if args.candidate_k is not None
        else service._candidate_top_k(
            args.top_k
        )
    )

    if candidate_top_k < args.top_k:
        raise ValueError(
            "--candidate-k must be greater "
            "than or equal to --top-k."
        )

    db = SessionLocal()

    try:
        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge Base not found: "
                f"{knowledge_base_id}"
            )

        print()
        print("=" * 100)
        print(
            "KNOWGENTIQ RERANKING DIAGNOSTIC"
        )
        print("=" * 100)

        print(
            f"Knowledge Base : "
            f"{knowledge_base_id}"
        )

        print(
            f"Query          : "
            f"{args.query}"
        )

        print(
            f"Candidate K    : "
            f"{candidate_top_k}"
        )

        print(
            f"Final K        : "
            f"{args.top_k}"
        )

        print(
            f"Reranker       : "
            f"{service.reranker_service.model_name}"
        )

        print("=" * 100)
        print()

        #
        # Stage 1:
        # semantic candidate retrieval
        #
        query_embedding = (
            service.embedding_service.embed(
                args.query
            )
        )

        candidates = (
            service
            .embedding_repository
            .search(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
                query_embedding=
                    query_embedding,
                top_k=
                    candidate_top_k,
            )
        )

        if not candidates:
            print(
                "No retrieval candidates "
                "found."
            )
            return

        #
        # Stage 2:
        # cross-encoder scoring
        #
        scored = (
            service.reranker_service.score(
                query=args.query,
                candidates=candidates,
            )
        )

        vector_rank_by_id = {}

        for rank, candidate in enumerate(
            candidates,
            start=1,
        ):
            chunk = candidate[0]

            vector_rank_by_id[
                chunk.id
            ] = rank

        print(
            "RERANKED CANDIDATES"
        )
        print(
            "-" * 100
        )

        for rerank_rank, (
            candidate,
            rerank_score,
        ) in enumerate(
            scored,
            start=1,
        ):
            chunk = candidate[0]
            document = candidate[1]
            source = candidate[2]
            distance = candidate[3]

            vector_rank = (
                vector_rank_by_id[
                    chunk.id
                ]
            )

            selected = (
                rerank_rank
                <= args.top_k
            )

            rank_delta = (
                vector_rank
                - rerank_rank
            )

            print()

            print(
                f"FINAL SELECTED : "
                f"{'YES' if selected else 'NO'}"
            )

            print(
                f"Rerank Rank    : "
                f"{rerank_rank}"
            )

            print(
                f"Vector Rank    : "
                f"{vector_rank}"
            )

            print(
                f"Rank Delta     : "
                f"{rank_delta:+d}"
            )

            print(
                f"Vector Distance: "
                f"{float(distance):.6f}"
            )

            print(
                f"Rerank Score   : "
                f"{rerank_score:.6f}"
            )

            print(
                f"Chunk ID       : "
                f"{chunk.id}"
            )

            print(
                f"Chunk Index    : "
                f"{chunk.chunk_index}"
            )

            print(
                f"Document       : "
                f"{getattr(document, 'name', None)}"
            )

            print(
                f"External ID    : "
                f"{getattr(document, 'external_id', None)}"
            )

            print(
                f"Source         : "
                f"{getattr(source, 'name', None)}"
            )

            print(
                "-" * 100
            )

            print(
                getattr(
                    chunk,
                    "text",
                    "",
                )
            )

            print(
                "-" * 100
            )

        print()
        print("=" * 100)
        print(
            "FINAL CONTEXT"
        )
        print("=" * 100)

        for final_rank, (
            candidate,
            rerank_score,
        ) in enumerate(
            scored[:args.top_k],
            start=1,
        ):
            chunk = candidate[0]
            document = candidate[1]

            vector_rank = (
                vector_rank_by_id[
                    chunk.id
                ]
            )

            rank_delta = (
                vector_rank
                - final_rank
            )

            print(
                f"{final_rank}. "
                f"vector_rank="
                f"{vector_rank} "
                f"rank_delta="
                f"{rank_delta:+d} "
                f"rerank_score="
                f"{rerank_score:.6f} "
                f"external_id="
                f"{getattr(document, 'external_id', None)} "
                f"chunk="
                f"{chunk.chunk_index}"
            )

        print()
        print("=" * 100)
        print(
            "COMPACT RANK COMPARISON"
        )
        print("=" * 100)

        for rerank_rank, (
            candidate,
            rerank_score,
        ) in enumerate(
            scored,
            start=1,
        ):
            chunk = candidate[0]
            document = candidate[1]

            vector_rank = (
                vector_rank_by_id[
                    chunk.id
                ]
            )

            selected_marker = (
                "*"
                if rerank_rank <= args.top_k
                else " "
            )

            print(
                f"{selected_marker} "
                f"vector={vector_rank:>2} "
                f"-> "
                f"rerank={rerank_rank:>2} "
                f"score={rerank_score:>10.6f} "
                f"chunk={chunk.chunk_index} "
                f"url="
                f"{getattr(document, 'external_id', None)}"
            )

        print()
        print(
            "* = selected for final context"
        )
        print("=" * 100)

    finally:
        db.close()


if __name__ == "__main__":
    main()