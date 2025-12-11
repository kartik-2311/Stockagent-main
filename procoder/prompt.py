"""Minimal `procoder.prompt` stub used by the project.

Provides lightweight implementations for the small API surface the app expects:
- NamedBlock
- NamedVariable
- Block
- SegmentedContent
- Collection

This is intentionally minimal: it favors returning a plain template string when
converted to `str()` so `procoder.functional.format_prompt` can call
`str(template).format(**kwargs)` to produce the final prompt text.
"""

from typing import Any


class NamedBlock:
    """A named block for prompt construction."""
    def __init__(self, refname: str | None = None, name: str | None = None, content: Any = None, **kwargs):
        self.refname = refname
        self.name = name
        self.content = content
        self.kwargs = kwargs

    def __repr__(self):
        return f"NamedBlock(name={self.name!r}, refname={self.refname!r})"


class NamedVariable:
    """A named variable for prompt construction."""
    def __init__(self, refname: str | None = None, name: str | None = None, content: Any = None, value: Any = None, description: str | None = None, **kwargs):
        self.refname = refname
        self.name = name
        self.content = content
        self.value = value
        self.description = description
        self.kwargs = kwargs

    def __repr__(self):
        return f"NamedVariable(refname={self.refname!r}, name={self.name!r})"


class Block:
    """Generic block wrapper."""
    def __init__(self, content: Any):
        self.content = content


class SegmentedContent:
    """Holds multiple segments of content."""
    def __init__(self, *segments: Any):
        self.segments = segments


class Collection:
    """Collection of prompt blocks.

    The real `procoder.Collection` offers indexing and rendering features; our
    stub implements `set_indexing_method` and `set_sep` for chaining, and
    `__str__` returns a simple joined template string made from children
    block `content` attributes so it can be formatted with `.format(**kwargs)`.
    """
    def __init__(self, *blocks: Any):
        self.blocks = list(blocks)
        self.indexing_method = None
        self.sep = "\n"

    def set_indexing_method(self, func):
        self.indexing_method = func
        return self

    def set_sep(self, sep: str):
        self.sep = str(sep)
        return self

    def __str__(self) -> str:
        parts = []
        for b in self.blocks:
            content = getattr(b, 'content', None)
            if content is None:
                parts.append(str(b))
            else:
                parts.append(str(content).strip())
        return self.sep.join(parts)


__all__ = [
    'NamedBlock',
    'NamedVariable',
    'Block',
    'SegmentedContent',
    'Collection',
    'sharp2_indexing',
]


def sharp2_indexing(collection):
    """Minimal stub for an indexing function.

    The real `sharp2_indexing` likely annotates or numbers blocks. For our
    purposes it's a no-op and returns the collection unchanged.
    """
    return collection
# end of procoder.prompt stub
