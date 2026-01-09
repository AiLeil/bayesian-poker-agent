import random
from typing import List
from dataclasses import dataclass

# ==========================================
# Constants (常量定义)
# ==========================================
# s=Spades(黑桃), h=Hearts(红桃), d=Diamonds(方块), c=Clubs(梅花)
SUITS = ['s', 'h', 'd', 'c']

# 2-9 是数字, T=10, J=Jack, Q=Queen, K=King, A=Ace
# 顺序很重要，用于后续比较大小
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


@dataclass(frozen=True)
class Card:
    """
    Card 类 (v2.0 Refactored)
    
    核心特性：
    1. Immutable (不可变): frozen=True 防止牌面在传递过程中被意外修改。
    2. Hashable (可哈希): 可以作为字典的 Key，或放入 set() 去重。
    3. Equality (相等性): Card('A','s') == Card('A','s') 自动为 True。
    """
    rank: str
    suit: str

    def __str__(self) -> str:
        """
        返回简短的字符串表示，例如 'As', 'Td'.
        这是 Treys 库能识别的格式。
        """
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        """
        调试时在列表里显示的格式。
        """
        return self.__str__()
    
    def to_int(self) -> int:
        """
        将牌转换为 0-51 的整数索引。
        
        用途：
        1. 用于机器学习模型的输入 (Embedding Layer)。
        2. 用于构建状态向量 (State Vector)。
        
        逻辑：
        2s=0, 2h=1, 2d=2, 2c=3 ... As=48, Ah=49...
        """
        rank_val = RANKS.index(self.rank)
        suit_val = SUITS.index(self.suit)
        return rank_val * 4 + suit_val


class Deck:
    """
    Deck 类表示一副标准的 52 张扑克牌。
    
    性能优化：
    使用 pop() (移除列表尾部) 代替 pop(0)，实现 O(1) 复杂度的发牌。
    """

    def __init__(self):
        self.cards: List[Card] = [] 
        self._initialize_deck()

    def _initialize_deck(self):
        """
        使用列表推导式生成 52 张牌，代码更紧凑高效。
        """
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        """
        随机洗牌。
        """
        random.shuffle(self.cards)

    def draw(self, n: int) -> List[Card]:
        """
        从牌堆顶（列表尾部）发 n 张牌。
        
        Complexity: O(n) —— 也就是 O(1) * n 次
        """
        if len(self.cards) < n:
            raise ValueError(f"牌不够了，剩余: {len(self.cards)}, 请求: {n}")
        
        drawn_cards = []
        for _ in range(n):
            # pop() 默认移除最后一个元素，无需移动其他元素内存，效率最高
            drawn_cards.append(self.cards.pop())
            
        return drawn_cards

    def __len__(self) -> int:
        return len(self.cards)