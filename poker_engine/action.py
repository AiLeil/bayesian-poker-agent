from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

class ActionType(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    RAISE = auto()
    ALL_IN = auto()

@dataclass
class Action:
    action_type: ActionType
    # Valid only for RAISE, represents the "Total Amount Raised To" (Raise To)
    amount: int = 0  

    def __str__(self):
        if self.action_type == ActionType.RAISE:
            return f"RAISE to {self.amount}"
        return self.action_type.name