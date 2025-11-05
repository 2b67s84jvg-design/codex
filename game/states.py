from __future__ import annotations

from enum import Enum, auto


class Screen(Enum):
    TITLE = auto()
    SELECTION = auto()
    BASE = auto()
    COMBAT_SELECT = auto()
    COMBAT = auto()
    BUILDING = auto()
    BREEDING = auto()
