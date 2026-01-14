from enum import Enum
from typing import List
from poker_engine.card import Card
from poker_engine.action import Action, ActionType

class PlayerState(Enum):
    """
    Enum representing the current state of a player.
    Used by the Game engine for state tracking.
    """
    ACTIVE = 0
    FOLDED = 1
    ALL_IN = 2
    OUT = 3  # Busted (0 chips)

class Player:
    """
    Base Player Class.
    Handles chip management, hand state, and action validation.
    """
    def __init__(self, id: int, name: str, stack: int):
        self.id = id
        self.name = name
        self.stack = stack
        self.hand: List[Card] = []
        self.folded = False
        self.all_in = False
        self.current_round_bet = 0
        self.total_bet_in_hand = 0
        self.state = PlayerState.ACTIVE # Track state with Enum as well

    def receive_cards(self, cards: List[Card]):
        self.hand = cards
        self.state = PlayerState.ACTIVE

    def reset_hand(self):
        """
        Resets the player's state for a new hand.
        """
        self.hand = []
        self.folded = False
        self.all_in = False
        self.current_round_bet = 0
        self.total_bet_in_hand = 0
        
        # Determine state based on stack
        if self.stack > 0:
            self.state = PlayerState.ACTIVE
        else:
            self.state = PlayerState.OUT

    def post_blind(self, amount: int) -> int:
        actual_amount = min(self.stack, amount)
        self.stack -= actual_amount
        self.current_round_bet += actual_amount
        self.total_bet_in_hand += actual_amount
        
        if self.stack == 0:
            self.all_in = True
            self.state = PlayerState.ALL_IN
            
        return actual_amount

    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        """
        Placeholder for decision logic. 
        Subclasses (BayesianAgent, RLAgent, BaselineAgent) must implement this.
        """
        raise NotImplementedError("Player subclass must implement get_action()")

    def __repr__(self):
        return f"Player({self.id}, {self.name}, Stack={self.stack}, State={self.state.name})"