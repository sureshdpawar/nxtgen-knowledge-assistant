import logging
import time

from functools import lru_cache

import torch

from sentence_transformers import (
    SentenceTransformer,
)

from app.core.constants import (
    EMBEDDING_MODEL,
)


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


@lru_cache(maxsize=1)
def get_embedding_model(
) -> SentenceTransformer:
    device = _get_device()

    started_at = (
        time.perf_counter()
    )

    logger.info(
        "Loading embedding model "
        "model='%s' device='%s'",
        EMBEDDING_MODEL,
        device,
    )

    model = SentenceTransformer(
        EMBEDDING_MODEL,
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
        "device='%s' "
        "load_ms=%.2f",
        EMBEDDING_MODEL,
        device,
        elapsed_ms,
    )

    return model


class EmbeddingService:

    def __init__(self):
        self.model = (
            get_embedding_model()
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
                EMBEDDING_MODEL,
                len(text),
                elapsed_ms,
            )
        else:
            logger.info(
                "Query embedding completed "
                "model='%s' "
                "text_length=%s "
                "embedding_ms=%.2f",
                EMBEDDING_MODEL,
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
                batch_size=
                    batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
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
            EMBEDDING_MODEL,
            len(texts),
            batch_size,
            elapsed_ms,
        )

        return (
            embeddings.tolist()
        )