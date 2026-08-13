"""State machine definition and transition validator for Controlled Research Agent."""

from enum import Enum
from typing import Union


class ResearchAgentState(str, Enum):
    """Execution states for the Controlled Research Agent."""

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    RETRIEVING = "RETRIEVING"
    ANALYZING = "ANALYZING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Dictionary mapping each state to allowed target states.
VALID_TRANSITIONS: dict[ResearchAgentState, set[ResearchAgentState]] = {
    ResearchAgentState.CREATED: {
        ResearchAgentState.PLANNING,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    },
    ResearchAgentState.PLANNING: {
        ResearchAgentState.RETRIEVING,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    },
    ResearchAgentState.RETRIEVING: {
        ResearchAgentState.ANALYZING,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    },
    ResearchAgentState.ANALYZING: {
        ResearchAgentState.VERIFYING,
        ResearchAgentState.RETRIEVING,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    },
    ResearchAgentState.VERIFYING: {
        ResearchAgentState.COMPLETED,
        ResearchAgentState.RETRIEVING,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    },
    ResearchAgentState.COMPLETED: set(),
    ResearchAgentState.FAILED: set(),
    ResearchAgentState.CANCELLED: set(),
}


class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""

    pass


def validate_state_transition(
    current: Union[str, ResearchAgentState],
    next_state: Union[str, ResearchAgentState],
) -> str:
    """Validate state transition for the Controlled Research Agent.

    Args:
        current: Current state as string or ResearchAgentState enum.
        next_state: Target state as string or ResearchAgentState enum.

    Returns:
        The validated target state value as a string.

    Raises:
        InvalidStateTransitionError: If either state is invalid or transition is illegal.
    """
    try:
        current_enum = (
            current
            if isinstance(current, ResearchAgentState)
            else ResearchAgentState(current)
        )
    except ValueError:
        raise InvalidStateTransitionError(f"Invalid current state: '{current}'")

    try:
        next_enum = (
            next_state
            if isinstance(next_state, ResearchAgentState)
            else ResearchAgentState(next_state)
        )
    except ValueError:
        raise InvalidStateTransitionError(f"Invalid target state: '{next_state}'")

    allowed_targets = VALID_TRANSITIONS.get(current_enum, set())
    if next_enum not in allowed_targets:
        raise InvalidStateTransitionError(
            f"Invalid state transition from '{current_enum.value}' to '{next_enum.value}'"
        )

    return next_enum.value
