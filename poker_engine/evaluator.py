# poker_engine/evaluator.py

from typing import List
from treys import Evaluator as TreysEvaluator
from treys import Card as TreysCard
from poker_engine.card import Card

class Ranker:
    """
    裁判类：负责计算牌力强弱。
    封装了 treys 库，提供简单的 score 接口。
    """
    def __init__(self):
        # 初始化 Treys 的评估器
        self.engine = TreysEvaluator()

    def score(self, hole_cards: List[Card], board_cards: List[Card]) -> int:
        """
        计算牌力分数。
        Treys 的分数越小越强 (1 = Royal Flush, 7462 = 7-2 offsuit)
        """
        # 1. 转换格式 (我们的 Card -> Treys 的 int)
        # 我们的 str() 是 'Ah', 'Tc' 这种，TreysCard.new() 正好接受这种字符串
        # 注意：这里我们要确保传入的是字符串
        t_hole = [TreysCard.new(str(c)) for c in hole_cards]
        t_board = [TreysCard.new(str(c)) for c in board_cards]

        # 2. 计算分数
        return self.engine.evaluate(t_board, t_hole)

    def get_rank_class(self, score: int) -> str:
        """
        把分数翻译成人类能听懂的牌型 (e.g. "Royal Flush")
        """
        rank_class = self.engine.get_rank_class(score)
        return self.engine.class_to_string(rank_class)