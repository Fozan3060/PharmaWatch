"""Auto-discovery of tools.

Importing this package walks every submodule and imports it, which fires the
@tool decorators and populates the registry. The orchestrator only needs to
import this package to get all tools registered.
"""

import importlib
import pkgutil

from app.agent.tools.base import all_tools, dispatch, to_gemini_function_declarations

__all__ = ["all_tools", "dispatch", "to_gemini_function_declarations"]


def _discover() -> None:
    package = __name__
    for module_info in pkgutil.walk_packages(__path__, prefix=f"{package}."):
        # Skip private modules (e.g. base.py is already imported above)
        if module_info.name.endswith(".base"):
            continue
        importlib.import_module(module_info.name)


_discover()
