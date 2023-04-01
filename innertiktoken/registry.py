from __future__ import annotations

import threading
from typing import Any, Callable, Optional

# import tiktoken_ext

from innertiktoken.core import Encoding
import innertiktoken.encoding_constructors as encoding_constructors

_lock = threading.RLock()
ENCODINGS: dict[str, Encoding] = {}
ENCODING_CONSTRUCTORS: Optional[dict[str, Callable[[], dict[str, Any]]]] = None

import inspect

def get_functions_from_module(module):
    functions = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            functions[name] = obj
    return functions



def _find_constructors() -> None:
    global ENCODING_CONSTRUCTORS
    ENCODING_CONSTRUCTORS = get_functions_from_module(encoding_constructors)

def get_encoding(encoding_name: str) -> Encoding:
    if encoding_name in ENCODINGS:
        return ENCODINGS[encoding_name]

    with _lock:
        if encoding_name in ENCODINGS:
            return ENCODINGS[encoding_name]

        if ENCODING_CONSTRUCTORS is None:
            _find_constructors()
            assert ENCODING_CONSTRUCTORS is not None

        if encoding_name not in ENCODING_CONSTRUCTORS:
            raise ValueError(f"Unknown encoding {encoding_name}")

        constructor = ENCODING_CONSTRUCTORS[encoding_name]
        enc = Encoding(**constructor())
        ENCODINGS[encoding_name] = enc
        return enc


def list_encoding_names() -> list[str]:
    with _lock:
        if ENCODING_CONSTRUCTORS is None:
            _find_constructors()
            assert ENCODING_CONSTRUCTORS is not None
        return list(ENCODING_CONSTRUCTORS)
