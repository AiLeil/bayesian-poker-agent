from enum import Enum
from typing import List, Optional
from poker_engine.card import Card

# ==========================================
# Enums (枚举状态)
# ==========================================
class PlayerState(Enum):
    """
    定义玩家在当前手牌中的状态。
    继承 Enum 类，类似于 Java 的 public enum PlayerState {...}
    """
    ACTIVE = 1   # 活跃状态 (还能下注/跟注)
    FOLDED = 2   # 已弃牌 (这手牌结束)
    ALL_IN = 3   # 全押 (无法再做动作，但拥有底池权益)
    OUT = 4      # 输光离场 (筹码归零)

class Player:
    """
    Player 类表示桌上的一个玩家。
    管理玩家的筹码(Stack)、手牌(Hand)和当前状态(State)。
    """

    def __init__(self, name: str, initial_stack: float):
        """
        初始化玩家。

        Args:
            name (str): 玩家的名字 (ID)。
            initial_stack (float): 初始筹码量。
        """
        self.name = name
        self.stack = initial_stack
        self.hand: List[Card] = []  # 玩家的手牌 (2张)
        self.state = PlayerState.ACTIVE
        
        # 记录这一轮下注了多少钱 (用于计算 Side Pot 或平账)
        self.current_bet = 0.0

    def receive_cards(self, cards: List[Card]):
        """
        接收手牌 (发牌阶段)。
        """
        self.hand = cards
        self.state = PlayerState.ACTIVE # 每次发牌时，状态重置为活跃

    def bet(self, amount: float) -> float:
        """
        玩家尝试下注 amount 金额。
        如果筹码不够，则自动转为 All-in。

        Args:
            amount (float): 想要下注的金额。

        Returns:
            float: 实际下注的金额 (如果是 All-in，可能小于 amount)。
        """
        if amount < 0:
            raise ValueError("下注金额不能为负数")

        # 逻辑：如果剩下的钱不够支付 amount，那就 All-in 剩下的所有钱
        if amount >= self.stack:
            actual_bet = self.stack
            self.stack = 0
            self.state = PlayerState.ALL_IN
        else:
            actual_bet = amount
            self.stack = self.stack - actual_bet
            # 状态保持 ACTIVE

        self.current_bet += actual_bet
        return actual_bet

    def fold(self):
        """
        玩家弃牌。
        """
        self.state = PlayerState.FOLDED
        self.hand = [] # 弃牌通常不亮牌，清空手牌 (可选逻辑)

    def reset_for_new_round(self):
        """
        在每一轮下注结束或新的一手牌开始时调用。
        重置当前下注额，但保留 stack。
        """
        self.current_bet = 0
        # 注意：不要在这里重置 hand 或 state，那通常是 start_hand 做的事

    def __str__(self):
        """
        显示玩家基础信息。
        例如: "Player(Gemini, stack=100.0, state=ACTIVE)"
        """
        # 注意：self.state.name 会获取枚举的名字 (如 'ACTIVE')
        return f"Player({self.name}, stack={self.stack}, state={self.state.name})"

    def __repr__(self):
        return self.__str__()