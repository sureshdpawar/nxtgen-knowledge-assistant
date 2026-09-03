from __future__ import annotations

import os

from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import (
    AsyncPostgresSaver,
)

from app.core.config import settings


# Current langgraph-checkpoint-postgres guidance recommends
# strict msgpack deserialization for persisted checkpoints.
os.environ.setdefault(
    "LANGGRAPH_STRICT_MSGPACK",
    "true",
)


def _checkpoint_database_uri() -> str:
    """
    LangGraph's Postgres saver uses Psycopg 3 directly.

    The main application currently uses SQLAlchemy + psycopg2.
    Keep those concerns separate and normalize only the driver
    marker if DATABASE_URL contains one.
    """

    uri = settings.DATABASE_URL

    uri = uri.replace(
        "postgresql+psycopg2://",
        "postgresql://",
        1,
    )

    uri = uri.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    if uri.startswith(
        "postgres://"
    ):
        uri = (
            "postgresql://"
            + uri[len("postgres://"):]
        )

    return uri


@asynccontextmanager
async def agent_checkpointer():
    """
    Yield the official LangGraph AsyncPostgresSaver.

    Knowgentiq does not implement checkpoint persistence.
    LangGraph owns checkpoint schema, writes, recovery,
    state history, interrupts, and resume semantics.
    """

    async with (
        AsyncPostgresSaver
        .from_conn_string(
            _checkpoint_database_uri()
        )
    ) as checkpointer:
        yield checkpointer


async def setup_agent_checkpointing() -> None:
    """
    Let LangGraph create/migrate its own checkpoint tables.

    These are framework-owned tables and intentionally are not
    recreated in Knowgentiq Alembic migrations.
    """

    async with agent_checkpointer() as checkpointer:
        await checkpointer.setup()
