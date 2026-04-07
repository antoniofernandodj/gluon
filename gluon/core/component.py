"""
@component decorator — turns a plain Python function into a Gluon component.

Two calling modes
-----------------
1. Inside a render tree (as a child):
       MyComponent(prop=value)
   Returns a VNode whose type is the original function.
   The renderer will later call the function with the fiber context set.

2. As the root argument to render():
       render(MyComponent, document.getElementById('root'))
   render() looks for the ._component_fn attribute to unwrap the wrapper.

Class-based fallback
--------------------
For components that are easier to express as classes, subclass Component
and implement render():

    class Clock(Component):
        def render(self):
            return div(p('…'))
"""

from gluon.core.vdom import VNode, _flatten


def component(fn):
    """
    Decorator: mark *fn* as a Gluon functional component.

    The returned wrapper, when called, creates a VNode rather than
    running the function immediately. The renderer will run *fn* at
    the right moment with the correct fiber context active.
    """
    def _call(*children, **props):
        key = props.pop('key', None)
        # children passed positionally end up in props['children']
        all_props = {**props, 'children': _flatten(children)}
        return VNode(fn, all_props, _flatten(children), key)

    _call._is_component = True
    _call._component_fn = fn        # renderer uses this to look up the fiber
    _call.__name__ = fn.__name__
    _call.__qualname__ = fn.__qualname__
    _call.__doc__ = fn.__doc__
    return _call


# ─── Class-based fallback ──────────────────────────────────────────────────────

class ComponentMeta(type):
    """Metaclass that makes Component subclasses behave like @component wrappers."""

    def __call__(cls, *children, **props):
        # When used as MyComponent(prop=…) in a tree → return VNode
        if _is_in_render_tree():
            key = props.pop('key', None)
            all_props = {**props, 'children': _flatten(children)}
            # Use cls itself as the VNode type; renderer detects Component subclass
            return VNode(cls, all_props, _flatten(children), key)
        # Otherwise instantiate normally (e.g. render(MyComponent, root))
        return super().__call__(*children, **props)


def _is_in_render_tree():
    """True when called during a render pass (fiber context is active)."""
    import gluon.core.fiber as _ctx
    return _ctx._current_fiber is not None


class Component(metaclass=ComponentMeta):
    """
    Base class for class-based components.

    Override render() to return a VNode tree.

    Example
    -------
        class Greeting(Component):
            def __init__(self, name='World'):
                self.name = name

            def render(self):
                return h1(f'Hello, {self.name}!')
    """

    # Marks the class so the renderer can identify it
    _is_component = True

    def __init__(self, **props):
        self.props = props

    def render(self):
        raise NotImplementedError("Component subclasses must implement render()")
