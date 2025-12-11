# Stub for procoder.functional
# This defines utility functions like format_prompt

def format_prompt(template, inputs=None, **kwargs):
    """Format a prompt template with given arguments.

    Supports being called as either `format_prompt(template, inputs_dict)`
    (the pattern used in the project) or `format_prompt(template, key=val, ...)`.
    """
    merged = {}
    if isinstance(inputs, dict):
        merged.update(inputs)
    # if inputs is not a dict but provided as a positional arg (e.g., None), ignore
    merged.update(kwargs)

    # If the template is a Collection-like object, pre-render any named variables
    # (blocks that expose a `refname` and `content`) so placeholders like
    # "{loan_type_prompt}" inside other blocks get replaced by the text of
    # the referenced NamedVariable.
    try:
        blocks = getattr(template, 'blocks', None)
        if blocks is not None:
            for b in blocks:
                ref = getattr(b, 'refname', None)
                content = getattr(b, 'content', None)
                if ref and content is not None:
                    # render the block content with the current merged mapping
                    try:
                        merged[ref] = str(content).format(**merged)
                    except Exception:
                        # If formatting fails (missing keys), keep raw content
                        merged[ref] = str(content)

    except Exception:
        # Be conservative: if anything goes wrong, fall back to naive formatting
        pass

    if callable(template):
        return template(**merged)
    return str(template).format(**merged)


__all__ = ['format_prompt']


def sharp2_indexing(collection):
    """Simple placeholder indexing function used by the code.

    The real implementation may add indices like '#1', '#2' etc. for blocks.
    For our stub we just return a function-like marker or None and do nothing.
    """
    return None
