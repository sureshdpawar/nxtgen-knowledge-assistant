import logging
import time

from functools import lru_cache

import torch

from sentence_transformers import (
    SentenceTransformer,
)

from app.core.config import settings


logger = logging.getLogger(
    "nxtgen.embedding"
)


SLOW_EMBEDDING_THRESHOLD_MS = 1000


def _get_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


@lru_cache(maxsize=4)
def get_embedding_model(
    model_name: str,
) -> SentenceTransformer:
    device = _get_device()

    started_at = (
        time.perf_counter()
    )

    logger.info(
        "Loading embedding model "
        "model='%s' "
        "dimensions=%s "
        "device='%s'",
        model_name,
        settings.EMBEDDING_DIMENSIONS,
        device,
    )

    model = SentenceTransformer(
        model_name,
        device=device,
    )

    elapsed_ms = (
        (
            time.perf_counter()
            - started_at
        )
        * 1000
    )

    logger.info(
        "Embedding model loaded "
        "model='%s' "
        "dimensions=%s "
        "device='%s' "
        "load_ms=%.2f",
        model_name,
        settings.EMBEDDING_DIMENSIONS,
        device,
        elapsed_ms,
    )

    return model


class EmbeddingService:

    def __init__(
        self,
        model_name: str | None = None,
    ):
        self.model_name = (
            model_name
            or settings.EMBEDDING_MODEL
        )

        self.model = (
            get_embedding_model(
                self.model_name,
            )
        )

    def embed(
        self,
        text: str,
    ) -> list[float]:
        started_at = (
            time.perf_counter()
        )

        embedding = (
            self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        )

        self._validate_dimensions(
            embedding,
        )

        elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        if (
            elapsed_ms
            >= SLOW_EMBEDDING_THRESHOLD_MS
        ):
            logger.warning(
                "Slow query embedding "
                "model='%s' "
                "text_length=%s "
                "embedding_ms=%.2f",
                self.model_name,
                len(text),
                elapsed_ms,
            )
        else:
            logger.info(
                "Query embedding completed "
                "model='%s' "
                "text_length=%s "
                "embedding_ms=%.2f",
                self.model_name,
                len(text),
                elapsed_ms,
            )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 32,
    ) -> list[list[float]]:
        if not texts:
            return []

        started_at = (
            time.perf_counter()
        )

        embeddings = (
            self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        )

        for embedding in embeddings:
            self._validate_dimensions(
                embedding,
            )

        elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        logger.info(
            "Batch embedding completed "
            "model='%s' "
            "items=%s "
            "batch_size=%s "
            "embedding_ms=%.2f",
            self.model_name,
            len(texts),
            batch_size,
            elapsed_ms,
        )

        return embeddings.tolist()

    def _validate_dimensions(
        self,
        embedding,
    ) -> None:
        actual_dimensions = len(
            embedding
        )

        expected_dimensions = (
            settings.EMBEDDING_DIMENSIONS
        )

        if (
            actual_dimensions
            != expected_dimensions
        ):
            raise ValueError(
                "Embedding dimension "
                "mismatch. "
                f"model='{self.model_name}' "
                f"expected="
                f"{expected_dimensions} "
                f"actual="
                f"{actual_dimensions}."
            )