"""
React-inspired hooks for Gluon components.

Phase 1: use_state
Phase 3 will add: use_effect, use_ref, use_memo, use_reducer, use_context
"""

from __future__ import annotations

from typing import Callable, TypeVar

import gluon.core.fiber as _ctx
from gluon.core.scheduler import schedule_rerender

T = TypeVar('T')


def use_state(initial: T | Callable[[], T]) -> tuple[T, Callable[[T | Callable[[T], T]], None]]:
    """
    Declare a piece of local state inside a functional component.

    Parameters
    ----------
    initial:
        The initial value (or a zero-argument factory callable).

    Returns
    -------
    (value, setter)
        value  - the current state value for this render.
        setter - call with a new value (or an updater function) to
                 trigger a re-render with the updated state.

    Example
    -------
        count, set_count = use_state(0)
        items, set_items = use_state(list)   # factory form
    """
    fiber = _ctx._current_fiber
    if fiber is None:
        raise RuntimeError(
            "use_state() was called outside of a @component render. "
            "Hooks must be called at the top level of a component function."
        )

    idx = fiber.hook_index
    fiber.hook_index += 1

    # First render: initialise the slot
    if len(fiber.hooks) <= idx:
        value = initial() if callable(initial) else initial
        fiber.hooks.append(value)

    def set_state(new_value: T | Callable[[T], T]) -> None:
        """
        Update state and schedule a re-render.

        Accepts either:
          set_state(42)            - replace with new value
          set_state(lambda v: v+1) - derive from previous value
        """
        current: T = fiber.hooks[idx]
        next_value: T = new_value(current) if callable(new_value) else new_value
        if next_value is not current:   # skip if identical object
            fiber.hooks[idx] = next_value
            schedule_rerender()

    return fiber.hooks[idx], set_state
