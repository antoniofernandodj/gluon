"""
Fiber: per-component-instance state container.

_current_fiber is a global variable set to the active fiber during
each component render pass, enabling hooks to associate state with
the correct component without being passed explicitly.
"""


# Set by the renderer right before calling a component function,
# cleared (or restored) immediately after. Hooks read this to know
# which fiber owns the current render.
_current_fiber = None


class Fiber:
    """
    Holds the persistent state for one component instance across renders.

    hooks       – list of values from every hook call (use_state, use_ref …)
    hook_index  – advances by 1 for each hook call; reset to 0 on each render
    """
    __slots__ = ('component_fn', 'hooks', 'hook_index')

    def __init__(self, component_fn):
        self.component_fn = component_fn
        self.hooks: list = []
        self.hook_index: int = 0
