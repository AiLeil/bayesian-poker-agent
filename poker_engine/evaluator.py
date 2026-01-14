from typing import List
from treys import Evaluator as TreysEvaluator
from treys import Card as TreysCard
from poker_engine.card import Card

class Ranker:
    """
    Referee Class: Responsible for calculating hand strength.
    Encapsulates the treys library, providing a simple score interface.
    """
    def __init__(self):
        # Initialize Treys evaluator
        self.engine = TreysEvaluator()

    def score(self, hole_cards: List[Card], board_cards: List[Card]) -> int:
        """
        Calculates hand strength score.
        Lower scores are stronger in Treys (1 = Royal Flush, 7462 = 7-2 offsuit).
        """
        # 1. Convert format (Our Card -> Treys int)
        # Our str() returns like 'Ah', 'Tc', which TreysCard.new() accepts directly.
        # Note: Ensure we are passing strings here.
        t_hole = [TreysCard.new(str(c)) for c in hole_cards]
        t_board = [TreysCard.new(str(c)) for c in board_cards]

        # 2. Calculate score
        return self.engine.evaluate(t_board, t_hole)

    def get_rank_class(self, score: int) -> str:
        """
        Translates score into human-readable hand type (e.g., "Royal Flush").
        """
        rank_class = self.engine.get_rank_class(score)
        return self.engine.class_to_string(rank_class)