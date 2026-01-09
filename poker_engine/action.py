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
    amount: int = 0  # 只有在 RAISE 时才有效，代表"加注到的总金额" (Raise To)

    def __str__(self):
        if self.action_type == ActionType.RAISE:
            return f"RAISE to {self.amount}"
        return self.action_type.name