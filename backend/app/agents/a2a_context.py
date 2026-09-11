from contextvars import ContextVar


# First slice deliberately supports one A2A delegation hop.
# This keeps the demo deterministic and prevents accidental cycles.
a2a_delegation_depth: ContextVar[int] = ContextVar(
    "knowgentiq_a2a_delegation_depth",
    default=0,
)
