"""Import-safe loading for the P2-B03 red tests.

Missing modules and AFC-STUB bodies fail by assertion so CMD-RED shows
behavioral red, never collection errors, import errors or skips.
"""

import importlib


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"lineup behavior is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"lineup behavior is not implemented (AFC-STUB): {exc}")
