import operator

from typing import (
    Annotated,
    NotRequired,
)

from langchain_core.messages import (
    BaseMessage,
)
from langgraph.graph.message import (
    add_messages,
)
from typing_extensions import (
    TypedDict,
)


class AgentState(TypedDict):
    # Durable conversational state. LangGraph's add_messages
    # reducer appends new messages while preserving message IDs.
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    # Per AgentRun execution counter. A new user turn resets it
    # to zero; interrupt/resume continues from the checkpoint.
    llm_calls: int

    # Trace data remains useful for the existing Knowgentiq run
    # audit UI. It is checkpointed so a resumed run can continue
    # without losing pre-interrupt execution steps.
    trace: Annotated[
        list[dict],
        operator.add,
    ]

    # Product correlation only. LangGraph still owns execution
    # persistence through thread_id/checkpoint_id in its config.
    active_run_id: str

    # Result of the current human approval interrupt.
    approval: NotRequired[
        dict | None
    ]
