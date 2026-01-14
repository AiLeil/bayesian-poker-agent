from dataclasses import dataclass
from typing import List

# ==========================================
# Constants
# ==========================================
# s=Spades, h=Hearts, d=Diamonds, c=Clubs
SUITS = ['s', 'h', 'd', 'c']

# Ranks: 2-9 are numbers, T=10, J=Jack, Q=Queen, K=King, A=Ace
# Order is critical for comparison logic
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

@dataclass(frozen=True)
class Card:
    """
    Card Class (Immutable & Hashable)
    
    Attributes:
        rank (str): '2'-'9', 'T', 'J', 'Q', 'K', 'A'
        suit (str): 's', 'h', 'd', 'c'
    """
    rank: str
    suit: str

    def __str__(self) -> str:
        """
        Returns short string representation compatible with Treys (e.g., 'As', 'Td').
        """
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def to_int(self) -> int:
        """
        Converts card to an integer index (0-51).
        Useful for Neural Network embeddings or State Vector construction.
        
        Logic: rank_index * 4 + suit_index
        """
        try:
            rank_val = RANKS.index(self.rank)
            suit_val = SUITS.index(self.suit)
            return rank_val * 4 + suit_val
        except ValueError:
            return -1