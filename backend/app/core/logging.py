import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    #
    # Reduce noisy third-party logs
    #
    logging.getLogger(
        "sqlalchemy.engine"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "httpx"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "httpcore"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "huggingface_hub"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "sentence_transformers"
    ).setLevel(
        logging.WARNING
    )

    #
    # Application logs
    #
    logging.getLogger(
        "nxtgen.request"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "nxtgen.search"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "nxtgen.embedding"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "nxtgen.llm"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "nxtgen.document_processing"
    ).setLevel(
        logging.INFO
    )