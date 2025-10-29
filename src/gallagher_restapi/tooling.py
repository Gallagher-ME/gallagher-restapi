"""Internal tooling utilities for function declaration generation."""

from __future__ import annotations

from typing import Any, Callable, TypeVar


F = TypeVar("F", bound=Callable[..., Any])


def expose_tool(func: F) -> F:
    """Mark a method/function as exposed for schema generation.

    Simply sets ``_exposed = True`` on the function and returns it unchanged.
    """
    setattr(func, "_exposed", True)
    return func


__all__ = ["expose_tool"]
