from enum import Enum, auto
from typing import List, Optional
from dataclasses import dataclass, field
from poker_engine.card import Card

# ==========================================
# Enums (状态机)
# ==========================================
class PlayerState(Enum):
    """
    玩家状态枚举。
    使用 auto() 自动赋值，后续如果想调整顺序或插入状态很方便。
    """
    ACTIVE = auto()   # 活跃：还在局中，可以思考和行动
    FOLDED = auto()   # 弃牌：这一局已经结束，只围观
    ALL_IN = auto()   # 全押：筹码已耗尽，等待开牌，不能再做动作
    OUT = auto()      # 出局：输光了所有身家，彻底离开游戏

# ==========================================
# Player Class
# ==========================================
@dataclass
class Player:
    """
    Player 类 (v2.0 Industrial Grade)
    
    设计重点：
    1. Mutable (可变): 玩家的筹码、手牌、状态随时在变，所以不用 frozen=True。
    2. Integer Money: 所有金额字段强制使用 int，避免浮点数精度误差。
    """
    name: str                  # 玩家ID/名字
    stack: int                 # 剩余筹码 (单位: 最小原子，如 '分')
    hand: List[Card] = field(default_factory=list)  # 玩家手牌
    state: PlayerState = PlayerState.ACTIVE         # 当前状态
    
    # 状态追踪字段
    current_round_bet: int = 0  # 这一轮(street)下了多少注 (用于计算还需要跟注多少)
    total_pot_contribution: int = 0 # 这一整局一共投入了多少 (用于分底池 Side Pot)

    def bet(self, amount: int) -> int:
        """
        玩家下注的核心逻辑。
        自动处理 All-in 情况。
        
        Args:
            amount: 想要下注的金额 (int)
            
        Returns:
            actual_bet: 实际下注成功的金额
        """
        if amount < 0:
            raise ValueError(f"下注金额不能为负数: {amount}")
        
        # 1. 检查是不是 All-in
        if amount >= self.stack:
            actual_bet = self.stack
            self.stack = 0
            self.state = PlayerState.ALL_IN
        else:
            actual_bet = amount
            self.stack -= actual_bet
            # 注意：状态保持 ACTIVE，除非之前就是 ALL_IN (理论上不可能)
            
        # 2. 更新统计数据
        self.current_round_bet += actual_bet
        self.total_pot_contribution += actual_bet
        
        return actual_bet

    def fold(self):
        """
        弃牌操作。
        """
        self.state = PlayerState.FOLDED
        self.hand = [] # 可选：弃牌后清空手牌，防止误判

    def receive_cards(self, cards: List[Card]):
        """
        新的一局开始，接收手牌。
        """
        self.hand = cards
        # 只有没输光的人才能由 OUT 变回 ACTIVE
        # 如果是 ALL_IN 状态结束上一局赢了钱，这里也重置为 ACTIVE
        if self.stack > 0:
            self.state = PlayerState.ACTIVE
        else:
            self.state = PlayerState.OUT

    def reset_round_state(self):
        """
        当进入下一轮 (e.g. Flop -> Turn) 时调用。
        清空当前轮的下注记录，但不清空总投入。
        """
        self.current_round_bet = 0

    def __str__(self):
        # 显示时稍微友好一点，带上状态
        return f"Player({self.name}, stack={self.stack}, state={self.state.name}, hand={self.hand})"

    def __repr__(self):
        return self.__str__()