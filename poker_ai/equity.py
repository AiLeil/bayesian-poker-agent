from typing import List, Tuple
import copy
import random
from poker_engine.card import Card, Deck
from poker_engine.evaluator import Ranker
from treys import Card as TreysCard

class EquityCalculator:
    def __init__(self):
        self.ranker = Ranker()

    def calculate_equity(self, hole_cards: List[Card], board_cards: List[Card], iterations: int = 1000) -> float:
        """
        蒙特卡洛模拟核心算法。
        
        Args:
            hole_cards: 我的手牌 (2张)
            board_cards: 当前公共牌 (0-5张)
            iterations: 模拟次数 (默认1000次)
            
        Returns:
            win_rate: 0.0 到 1.0 之间的浮点数
        """
        # 1. 弄一副完整的牌
        full_deck = Deck()
        
        # 2. 从牌堆里剔除掉已知牌 (手牌 + 公共牌)
        # 这是一个优化点：我们不需要真的去 shuffle 整个对象，
        # 只需要知道哪些牌是"未知"的。
        known_cards = set(str(c) for c in hole_cards + board_cards)
        unknown_deck = [c for c in full_deck.cards if str(c) not in known_cards]

        wins = 0
        
        # 需要补几张牌才能凑齐5张公牌？
        cards_to_deal = 5 - len(board_cards)
        
        # 如果已经发完河牌了，直接算结果，不用模拟
        if cards_to_deal == 0:
            return self._calculate_showdown_strength(hole_cards, board_cards, unknown_deck)

        # 3. 开始疯狂模拟
        for _ in range(iterations):
            # 随机抽样 (相当于发剩下的 Turn/River)
            # random.sample 不会改变原列表，速度很快
            runout = random.sample(unknown_deck, cards_to_deal)
            
            # 模拟出来的完整公牌
            simulated_board = board_cards + runout
            
            # 模拟对手的手牌 (随机抽2张)
            # 注意：这里的逻辑是假设对手是"随机牌" (Random Hand)。
            # 在贝叶斯更新中，我们会把这里改成"对手的范围" (Range)。
            remaining_for_opp = [c for c in unknown_deck if c not in runout]
            opp_hole = random.sample(remaining_for_opp, 2)
            
            # 4. 比大小
            my_score = self.ranker.score(hole_cards, simulated_board)
            opp_score = self.ranker.score(opp_hole, simulated_board)
            
            if my_score < opp_score: # Treys 分数越低越好
                wins += 1
            elif my_score == opp_score:
                wins += 0.5 # 平分底池算赢一半
                
        return wins / iterations

    def _calculate_showdown_strength(self, my_hole, board, unknown_deck):
        """
        当没有牌可发时 (River)，计算针对随机对手的胜率。
        """
        my_score = self.ranker.score(my_hole, board)
        wins = 0
        iterations = 100 # 这种情况我们可以精确一点，或者模拟少一点
        
        for _ in range(iterations):
            opp_hole = random.sample(unknown_deck, 2)
            opp_score = self.ranker.score(opp_hole, board)
            if my_score < opp_score:
                wins += 1
            elif my_score == opp_score:
                wins += 0.5
        
        return wins / iterations