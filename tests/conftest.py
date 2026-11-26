"""Load the integration's pure-Python modules without Home Assistant.

logic.py and const.py do not import Home Assistant, but the package's
__init__.py does. Register the folder as a bare package so the tests can
import saison_themes.logic without executing __init__.py.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "saison_themes"

if "saison_themes" not in sys.modules:
    pkg = types.ModuleType("saison_themes")
    pkg.__path__ = [str(_PKG_DIR)]
    sys.modules["saison_themes"] = pkg
