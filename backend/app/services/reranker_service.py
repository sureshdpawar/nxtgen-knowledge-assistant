import logging
import threading
import time

from typing import Any

from sentence_transformers import (
    CrossEncoder,
)

from app.core.config import settings


logger = logging.getLogger(
    "nxtgen.reranker"
)


class RerankerService:

    _models: dict[
        str,
        CrossEncoder,
    ] = {}

    _models_lock = threading.Lock()

    def __init__(
        self,
        model_name: str | None = None,
    ):
        self.model_name = (
            model_name
            or settings.RERANKER_MODEL
        )

    def rerank(
        self,
        query: str,
        candidates: list[Any],
        top_k: int,
    ) -> list[Any]:
        if top_k < 1:
            raise ValueError(
                "top_k must be "
                "greater than 0."
            )

        if not candidates:
            return []

        if len(candidates) == 1:
            return candidates[:top_k]

        scored_candidates = (
            self.score(
                query=query,
                candidates=candidates,
            )
        )

        return [
            candidate
            for candidate, _
            in scored_candidates[:top_k]
        ]

    def score(
        self,
        query: str,
        candidates: list[Any],
    ) -> list[
        tuple[Any, float]
    ]:
        if not candidates:
            return []

        if len(candidates) == 1:
            return [
                (
                    candidates[0],
                    1.0,
                )
            ]

        model = self._get_model()

        pairs = [
            (
                query,
                self._candidate_text(
                    candidate,
                ),
            )
            for candidate in candidates
        ]

        started_at = (
            time.perf_counter()
        )

        scores = model.predict(
            pairs,
            show_progress_bar=False,
        )

        elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        scored_candidates = [
            (
                candidate,
                float(score),
            )
            for candidate, score
            in zip(
                candidates,
                scores,
                strict=True,
            )
        ]

        scored_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        logger.info(
            "Reranking completed "
            "model='%s' "
            "candidates=%s "
            "rerank_ms=%.2f",
            self.model_name,
            len(candidates),
            elapsed_ms,
        )

        return scored_candidates

    def _get_model(
        self,
    ) -> CrossEncoder:
        model = self._models.get(
            self.model_name
        )

        if model is not None:
            return model

        with self._models_lock:
            model = self._models.get(
                self.model_name
            )

            if model is not None:
                return model

            started_at = (
                time.perf_counter()
            )

            logger.info(
                "Loading reranker model "
                "model='%s'",
                self.model_name,
            )

            model = CrossEncoder(
                self.model_name
            )

            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            self._models[
                self.model_name
            ] = model

            logger.info(
                "Reranker model loaded "
                "model='%s' "
                "load_ms=%.2f",
                self.model_name,
                elapsed_ms,
            )

            return model

    @staticmethod
    def _candidate_text(
        candidate: Any,
    ) -> str:
        chunk = candidate[0]

        return chunk.text