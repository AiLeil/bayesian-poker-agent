from enum import Enum, auto
from typing import List, Optional
from dataclasses import dataclass, field
from poker_engine.card import Card
from poker_engine.action import Action, ActionType

# 保持 Enums 不变
class PlayerState(Enum):
    ACTIVE = auto()
    FOLDED = auto()
    ALL_IN = auto()
    OUT = auto()

@dataclass
class Player:
    """
    Player 基类。
    不再包含具体的 get_action 实现，而是留给子类。
    """
    name: str
    stack: int
    hand: List[Card] = field(default_factory=list)
    state: PlayerState = PlayerState.ACTIVE
    
    current_round_bet: int = 0
    total_pot_contribution: int = 0

    # === 通用方法 (保持不变) ===
    def bet(self, amount: int) -> int:
        if amount < 0: raise ValueError(f"下注金额不能为负数: {amount}")
        if amount >= self.stack:
            actual_bet = self.stack
            self.stack = 0
            self.state = PlayerState.ALL_IN
        else:
            actual_bet = amount
            self.stack -= actual_bet
        
        self.current_round_bet += actual_bet
        self.total_pot_contribution += actual_bet
        return actual_bet

    def fold(self):
        self.state = PlayerState.FOLDED
        self.hand = []

    def receive_cards(self, cards: List[Card]):
        self.hand = cards
        if self.stack > 0:
            self.state = PlayerState.ACTIVE
        else:
            self.state = PlayerState.OUT

    def reset_round_state(self):
        self.current_round_bet = 0

    # === 核心修改：抽象接口 ===
    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        """
        子类必须实现这个方法。
        注意：我们增加了 'pot' 和 'board' 参数，因为 AI 需要看公牌算胜率！
        """
        raise NotImplementedError("Player 是基类，请使用 HumanPlayer 或 AutoAgent")

    def __str__(self):
        return f"{self.name}({self.stack})"
    def __repr__(self):
        return self.__str__()

# === 人类玩家实现 ===
@dataclass
class HumanPlayer(Player):
    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        to_call = current_bet - self.current_round_bet
        print(f"\n>> 轮到 {self.name} (Human) 了 (Stack: {self.stack})")
        print(f"   Hand: {self.hand}")
        print(f"   Board: {board}")
        print(f"   Pot: {pot}, To Call: {to_call}")

        while True:
            cmd = input(f"   请输入动作 (f/c/r [amount]/a): ").strip().lower()
            if cmd == 'f': return Action(ActionType.FOLD)
            elif cmd == 'c':
                return Action(ActionType.CHECK) if to_call == 0 else Action(ActionType.CALL)
            elif cmd == 'a': return Action(ActionType.ALL_IN)
            elif cmd.startswith('r'):
                try:
                    parts = cmd.split()
                    if len(parts) < 2: continue
                    amt = int(parts[1])
                    if amt < min_raise:
                        print(f"   [!] 最小加注: {min_raise}")
                        continue
                    return Action(ActionType.RAISE, amount=amt)
                except ValueError: pass
            else:
                print("   [!] 未知指令")