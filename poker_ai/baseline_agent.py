from poker_engine.player import Player
from poker_engine.action import Action, ActionType
from poker_ai.equity import EquityCalculator
from poker_engine.card import Card
import random

class BaselineAgent(Player):
    """
    Standard 'ABC Poker' Agent with slight noise.
    """
    def __init__(self, id, name, stack):
        super().__init__(id, name, stack)
        self.brain = EquityCalculator()

    def get_action(self, current_bet, min_raise, pot, board):
        # Reduce simulation count to speed up training (50 is enough to distinguish good/bad hands)
        equity = self.brain.calculate_equity(self.hand, board, iterations=50)
        
        to_call = current_bet - self.current_round_bet
        final_pot = pot + to_call + to_call
        pot_odds = to_call / final_pot if final_pot > 0 else 0

        # === Add 10% random noise to prevent RL overfitting ===
        if random.random() < 0.1:
            # 10% chance to play randomly (simulating a fish or bluffing)
            if to_call == 0: return Action(ActionType.CHECK)
            return Action(ActionType.CALL)

        # Standard ABC Logic
        if equity > 0.75: # Slightly increase raise threshold for stability
            amount = int(pot * 0.6) # Raise 60% of the pot
            actual_amount = max(amount, min_raise)
            total = actual_amount + self.current_round_bet
            if total >= self.stack + self.current_round_bet:
                return Action(ActionType.ALL_IN)
            return Action(ActionType.RAISE, amount=total)

        if equity >= pot_odds:
            if to_call == 0: return Action(ActionType.CHECK)
            return Action(ActionType.CALL)

        if to_call == 0:
            return Action(ActionType.CHECK)
        else:
            return Action(ActionType.FOLD)