import random
from typing import List

# ==========================================
# Constants (常量定义)
# ==========================================
# s=Spades(黑桃), h=Hearts(红桃), d=Diamonds(方块), c=Clubs(梅花)
SUITS = ['s', 'h', 'd', 'c']

# 2-9 是数字, T=10, J=Jack, Q=Queen, K=King, A=Ace
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


class Card:
    """
    Card 类表示一张扑克牌。
    这是一个基础的数据类，只包含牌的大小(rank)和花色(suit)。
    """

    def __init__(self, rank: str, suit: str):
        """
        初始化一张扑克牌。

        Args:
            rank (str): 牌的大小，必须在 RANKS 列表中 (例如 'A', 'K', '2')。
            suit (str): 牌的花色，必须在 SUITS 列表中 (例如 's', 'h')。
        """
        # 相当于 Java: this.rank = rank;
        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        """
        返回这张牌的用户可读字符串表示。
        
        Returns:
            str: 例如 'As' (黑桃A) 或 'Td' (方块10)。
        """
        # 基础字符串拼接
        return self.rank + self.suit

    def __repr__(self) -> str:
        """
        返回这张牌的调试用字符串表示。
        当在一个列表里打印牌时，会调用这个方法。
        """
        return self.__str__()


class Deck:
    """
    Deck 类表示一副标准的 52 张扑克牌。
    提供了洗牌(shuffle)和发牌(draw)的功能。
    """

    def __init__(self):
        """
        初始化一副新的扑克牌。
        在创建时会自动生成 52 张牌并按顺序排列。
        """
        # 相当于 Java: List<Card> cards = new ArrayList<>();
        self.cards: List[Card] = [] 
        self._initialize_deck()

    def _initialize_deck(self):
        """
        [内部方法] 生成 52 张牌并填充到 self.cards 列表中。
        使用双重循环遍历所有的花色和大小。
        """
        for suit in SUITS:
            for rank in RANKS:
                new_card = Card(rank, suit)
                self.cards.append(new_card)

    def shuffle(self):
        """
        随机打乱牌堆中的牌序。
        直接修改 self.cards 列表。
        """
        random.shuffle(self.cards)

    def draw(self, n: int) -> List[Card]:
        """
        从牌堆顶部（列表尾部）抽取 n 张牌。

        Args:
            n (int): 需要抽取的张数。

        Returns:
            List[Card]: 一个包含 n 张 Card 对象的列表。

        Raises:
            ValueError: 如果牌堆剩余数量少于 n 张，则抛出此异常。
        """
        # 检查剩余牌数是否足够
        if len(self.cards) < n:
            # 基础字符串格式化，用来显示错误信息
            msg = "牌不够了，剩余: " + str(len(self.cards)) + ", 请求: " + str(n)
            raise ValueError(msg)
        
        drawn_cards = []
        # 循环 n 次，每次拿一张
        for i in range(n):
            # pop() 默认移除列表的最后一个元素，效率最高 (O(1))
            card = self.cards.pop()
            drawn_cards.append(card)
            
        return drawn_cards

    def __len__(self) -> int:
        """
        返回当前牌堆剩余的牌数。
        允许使用 len(deck) 语法。
        """
        return len(self.cards)