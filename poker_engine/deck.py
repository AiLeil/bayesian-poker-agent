import random
from typing import List
from poker_engine.card import Card, SUITS, RANKS

class Deck:
    """
    Represents a standard 52-card deck.
    Optimized for O(1) drawing using list.pop().
    """

    def __init__(self):
        self.cards: List[Card] = [] 
        self._initialize_deck()

    def _initialize_deck(self):
        """
        Generates 52 cards using list comprehension.
        """
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        """
        Randomizes the order of cards.
        """
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        """
        Draws n cards from the top of the deck (end of list).
        
        Complexity: O(n) due to O(1) per pop operation.
        """
        if len(self.cards) < n:
            # Auto-reset if deck runs out (safety mechanism for long simulations)
            self.reset()
            if len(self.cards) < n:
                raise ValueError(f"Deck error: Requested {n}, but deck empty.")
        
        drawn_cards = []
        for _ in range(n):
            # pop() removes the last element, no memory shift required.
            drawn_cards.append(self.cards.pop())
            
        return drawn_cards

    def reset(self):
        """
        Re-initializes and shuffles the deck.
        """
        self._initialize_deck()
        self.shuffle()

    def __len__(self) -> int:
        return len(self.cards)