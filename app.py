"""
Gluon — Phase 1 demo app.

Demonstrates:
  - Functional components with @component
  - use_state hook
  - Event handling (onClick)
  - Nested components
  - Props passing
  - list comprehension as children
"""

from __future__ import annotations

from typing import Callable

from gluon import component, use_state, render
from gluon import div, h1, h2, h3, p, button, span, ul, li, input, label, hr, strong
from gluon.core.vdom import VNode
from js import document, Event, KeyboardEvent


# ─── Type aliases for state setters ────────────────────────────────────────────
IntSetter = Callable[[int | Callable[[int], int]], None]
ListSetter = Callable[[list[str] | Callable[[list[str]], list[str]]], None]
StrSetter = Callable[[str | Callable[[str], str]], None]


# ─── Reusable components ───────────────────────────────────────────────────────

@component
def Badge(text: str, color: str = '#0077ff') -> VNode:
    return span(
        text,
        style={
            'background': color,
            'color': 'white',
            'padding': '2px 10px',
            'border-radius': '12px',
            'font-size': '0.8rem',
            'font-weight': 'bold',
        }
    )


@component
def Counter(title: str = 'Counter', initial: int = 0) -> VNode:
    count: int
    set_count: IntSetter
    count, set_count = use_state(initial)

    def decrement(e: Event) -> None:
        set_count(lambda n: n - 1)

    def increment(e: Event) -> None:
        set_count(lambda n: n + 1)

    def reset(e: Event) -> None:
        set_count(initial)

    color: str = '#27ae60' if count > 0 else ('#e74c3c' if count < 0 else '#7f8c8d')

    return div(
        h3(title),
        div(
            button('-', onClick=decrement, style={'font-size': '1.2rem', 'padding': '4px 12px'}),
            span(
                str(count),
                style={'font-size': '1.5rem', 'font-weight': 'bold', 'color': color,
                       'margin': '0 16px', 'min-width': '3ch', 'display': 'inline-block',
                       'text-align': 'center'},
            ),
            button('+', onClick=increment, style={'font-size': '1.2rem', 'padding': '4px 12px'}),
            button('reset', onClick=reset, style={'margin-left': '12px', 'padding': '4px 10px'}),
            style={'display': 'flex', 'align-items': 'center', 'gap': '4px'},
        ),
        style={
            'border': '1px solid #ddd',
            'border-radius': '8px',
            'padding': '16px',
            'margin': '12px 0',
            'background': '#fafafa',
        }
    )


@component
def TodoList() -> VNode:
    todos: list[str]
    set_todos: ListSetter
    todos, set_todos = use_state(['Buy groceries', 'Write some Python'])

    text: str
    set_text: StrSetter
    text, set_text = use_state('')

    def on_input(e: Event) -> None:
        set_text(e.target.value)

    def add_todo(e: Event) -> None:
        t = text.strip()
        if t:
            set_todos(lambda lst: [*lst, t])
            set_text('')

    def remove(idx: int) -> Callable[[Event], None]:
        def handler(e: Event) -> None:
            set_todos(lambda lst: [item for i, item in enumerate(lst) if i != idx])
        return handler

    def on_keydown(e: KeyboardEvent) -> None:
        if e.key == 'Enter':
            add_todo(e)

    return div(
        h3('Todo List  ', Badge(f'{len(todos)} items')),
        div(
            input(
                type='text',
                value=text,
                onInput=on_input,
                onKeyDown=on_keydown,
                placeholder='New task…',
                style={'padding': '6px 10px', 'flex': '1', 'border': '1px solid #ccc',
                       'border-radius': '4px', 'font-size': '1rem'},
            ),
            button('Add', onClick=add_todo,
                   style={'padding': '6px 14px', 'background': '#0077ff', 'color': 'white',
                          'border': 'none', 'border-radius': '4px', 'cursor': 'pointer'}),
            style={'display': 'flex', 'gap': '8px', 'margin-bottom': '10px'},
        ),
        ul(
            *[
                li(
                    span(todo, style={'flex': '1'}),
                    button('✕', onClick=remove(idx),
                           style={'background': 'none', 'border': 'none', 'color': '#e74c3c',
                                  'cursor': 'pointer', 'font-size': '1rem'}),
                    style={'display': 'flex', 'align-items': 'center',
                           'padding': '6px 0', 'border-bottom': '1px solid #eee'},
                )
                for idx, todo in enumerate(todos)
            ],
            style={'list-style': 'none', 'padding': '0', 'margin': '0'},
        ) if todos else p('No tasks yet!', style={'color': '#aaa', 'font-style': 'italic'}),
        style={
            'border': '1px solid #ddd',
            'border-radius': '8px',
            'padding': '16px',
            'margin': '12px 0',
            'background': '#fafafa',
        }
    )


# ─── Root app ──────────────────────────────────────────────────────────────────

@component
def App() -> VNode:
    return div(
        h1('🧪 Gluon', style={'margin-bottom': '4px'}),
        p(
            'A React-inspired Python UI framework running on WebAssembly via PyScript.',
            style={'color': '#555', 'margin-top': '0'},
        ),
        hr(),
        h2('Counters'),
        Counter(title='Basic Counter'),
        Counter(title='Another Counter', initial=10),
        hr(),
        h2('Todo List'),
        TodoList(),
        style={
            'font-family': 'system-ui, sans-serif',
            'max-width': '600px',
            'margin': '32px auto',
            'padding': '0 16px',
        }
    )


render(App, document.getElementById('root'))
