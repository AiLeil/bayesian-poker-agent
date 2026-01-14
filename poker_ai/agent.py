from dataclasses import dataclass, field
from typing import List, Dict
import itertools
import math
import random

from treys import Card as TreysCard
from treys import Evaluator
from poker_engine.player import Player
from poker_engine.action import Action, ActionType
from poker_engine.card import Card
# Correct import to avoid circular dependency
from poker_ai.equity import EquityCalculator 

# ==========================================
# 1. Base Class: AutoAgent 
# ==========================================
class AutoAgent(Player):
    """
    A simple autonomous agent that plays based on simple heuristic rules.
    Acts as a base class for the BayesianAgent.
    """
    def __init__(self, id, name, stack):
        super().__init__(id, name, stack)

    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        # Fallback logic: Check if possible, otherwise Call
        to_call = current_bet - self.current_round_bet
        if to_call == 0:
            return Action(ActionType.CHECK)
        else:
            return Action(ActionType.CALL)

# ==========================================
# 2. Main Class: BayesianAgent
# ==========================================
@dataclass
class BayesianAgent(AutoAgent):
    """
    Agent V3.5 (Heads-Up Optimized): 
    - Tiered HU Prior (Better cold start)
    - Mixed Strategy (Trapping/Bluffing)
    - Sigmoid Likelihood
    - Memory Decay
    """
    opponent_belief: Dict[str, float] = field(default_factory=dict)
    evaluator: Evaluator = field(default_factory=Evaluator, init=False)
    
    # Memory: {"RAISE": 5, "FOLD": 2, "CALL": 10}
    history_stats: Dict[str, int] = field(default_factory=lambda: {"RAISE": 0, "CALL": 0, "CHECK": 0, "FOLD": 0})
    
    # Decay Factor: 0.95 (Adapt to non-stationary opponents)
    memory_decay: float = 0.95 

    def __post_init__(self):
        pass

    def __init__(self, id, name, stack, **kwargs):
        super().__init__(id, name, stack)
        self.evaluator = Evaluator()
        self.brain = EquityCalculator()
        self.opponent_belief = {}
        self.history_stats = {"RAISE": 0, "CALL": 0, "CHECK": 0, "FOLD": 0}
        self.memory_decay = 0.95
        self.reset_belief()
        self.opponent_aggressiveness = 1.0 # 1.0=Standard, <1.0=Passive(TP), >1.0=Aggressive(LAG)

    def receive_cards(self, cards: List[Card]):
        super().receive_cards(cards)
        self.reset_belief()

    # === New Method: Showdown Analysis ===
    def analyze_showdown(self, opponent_hand_cards: List[Card], board: List[Card], final_action: str):
        """
        Adjust judgement of opponent's personality based on their showdown hand strength vs last action.
        """
        # 1. Calculate actual hand strength (0~1)
        # Convert Card objects to Treys format
        board_treys = [TreysCard.new(str(c)) for c in board]
        hand_treys = [TreysCard.new(str(c)) for c in opponent_hand_cards]
        
        score = self.evaluator.evaluate(board_treys, hand_treys)
        strength = 1.0 - (score / 7462.0) # 1.0 is Royal Flush, 0.0 is trash
        
        print(f"[Showdown Analysis] Opponent had strength {strength:.2f} and action was {final_action}")

        # 2. Bayesian Reflection: If I were them, what would I do with this strength?
        # 3. Aggressiveness Correction
        
        # Case A: Opponent has strong hand (Strength > 0.8) but only CHECK/CALL
        # Conclusion: Opponent is TP/LP (Trapping/Passive), lower aggression expectation
        if strength > 0.8 and final_action in ['CHECK', 'CALL']:
            self.opponent_aggressiveness *= 0.9
            print("   -> Detected PASSIVE play with monster. Lowering aggression expectation.")

        # Case B: Opponent has trash (Strength < 0.4) but RAISE/ALL_IN
        # Conclusion: Opponent is LAG/Maniac (Bluffing), increase aggression expectation
        elif strength < 0.4 and final_action in ['RAISE', 'ALL_IN']:
            self.opponent_aggressiveness *= 1.1
            print("   -> Detected BLUFF with trash. Increasing aggression expectation.")
        
        # Clamp values to prevent explosion
        self.opponent_aggressiveness = max(0.5, min(2.0, self.opponent_aggressiveness))
        print(f"   -> New Opponent Aggressiveness Index: {self.opponent_aggressiveness:.2f}")

    def reset_belief(self):
        # OPTIMIZATION 1: Use Heads-Up specific prior instead of uniform
        raw_belief = self._init_hu_prior()
        total = sum(raw_belief.values())
        self.opponent_belief = {k: v / total for k, v in raw_belief.items()}

    def _init_hu_prior(self):
        """
        Heads-Up Population Tendency Prior.
        In HU, players play much wider ranges (VPIP ~50-80%).
        We assign weights based on hand tier.
        """
        belief = {}
        ranks = "23456789TJQKA"
        
        # Helper to categorize hands
        def get_weight(r1, r2, is_suited):
            # Tier 1: Monster (Pairs 88+, Big Aces, KQs) -> Always played (1.0)
            if r1 == r2 and r1 in "89TJQKA": return 1.0
            if r1 in "AK" and r2 in "AKQJ": return 1.0
            
            # Tier 2: Playable (Any Pair, Any Ace, Suited Connectors, Broadways) -> High freq (0.8)
            if r1 == r2: return 0.8 # Low pairs
            if r1 == 'A' or r2 == 'A': return 0.8 # Any Ace is strong in HU
            if r1 in "KQJ" and r2 in "KQJT9": return 0.7 # Broadways
            if is_suited and abs(ranks.index(r1) - ranks.index(r2)) <= 2: return 0.7 # Suited connectors
            
            # Tier 3: Marginal (Kx, Qx, Suited junk) -> Moderate freq (0.4)
            if r1 == 'K' or r2 == 'K': return 0.4
            if is_suited: return 0.4
            
            # Tier 4: Trash (Offsuit gappers) -> Low freq (0.1)
            return 0.1

        # Generate all combos
        for r in ranks: 
            belief[r + r] = get_weight(r, r, False)
        
        for i in range(len(ranks)):
            for j in range(i):
                r1, r2 = ranks[i], ranks[j] # r1 is higher rank
                belief[f"{r1}{r2}s"] = get_weight(r1, r2, True)
                belief[f"{r1}{r2}o"] = get_weight(r1, r2, False)
                
        return belief

    def observe_action(self, actor_id: int, action: Action, board: List[Card]):
        if actor_id != self.id:
            # === Memory Decay Update ===
            for k in self.history_stats:
                self.history_stats[k] *= self.memory_decay
            
            action_name = action.action_type.name
            current_val = self.history_stats.get(action_name, 0.0)
            self.history_stats[action_name] = current_val + 1.0
            
            # print(f"[Bayes] Observed opponent action: {action_name}")
            self._update_belief(action, board)

    def _update_belief(self, action: Action, board: List[Card]):
        total_probability = 0
        new_belief = {}
        is_preflop = (len(board) == 0)
        board_treys = [TreysCard.new(str(c)) for c in board]

        bluff_prob = self._calculate_bluff_probability()

        for hand_str, prior_prob in self.opponent_belief.items():
            likelihood = self._get_smart_likelihood(hand_str, action, board_treys, is_preflop, bluff_prob)
            
            unnormalized_posterior = likelihood * prior_prob
            new_belief[hand_str] = unnormalized_posterior
            total_probability += unnormalized_posterior

        if total_probability > 0:
            for hand in new_belief: new_belief[hand] /= total_probability
            self.opponent_belief = new_belief
        else:
            # print(f"[Warning] Impossible event observed. Resetting belief priors.")
            self.reset_belief()

    def _calculate_bluff_probability(self) -> float:
        total_actions = sum(self.history_stats.values())
        if total_actions < 5.0: return 0.10 # Default slightly higher for HU

        raise_count = self.history_stats.get("RAISE", 0)
        raise_freq = raise_count / total_actions
        
        # In Heads-Up, aggression is higher. Adjust thresholds.
        if raise_freq > 0.4: return 0.30
        if raise_freq > 0.6: return 0.50
        return 0.10

    def _get_smart_likelihood(self, hand_str: str, action: Action, board_treys: List[int], is_preflop: bool, bluff_prob: float) -> float:
        """
        Calculates P(Action | Hand Strength, Opponent Style).
        Uses Sigmoid functions dynamically shifted by 'opponent_aggressiveness'.
        """
        # 1. Calculate raw hand strength (0.0 to 1.0)
        strength = 0.5
        if is_preflop:
            strength = self._get_preflop_strength(hand_str)
        else:
            strength = self._get_postflop_strength(hand_str, board_treys)

        # 2. Dynamic Curve Fitting based on Opponent Profile
        # opponent_aggressiveness: 
        #   < 1.0 (Passive/Tight-Passive): Needs higher strength to raise, more likely to trap.
        #   > 1.0 (Aggressive/LAG): Raises with wider range, less likely to trap.
        #   = 1.0 (Standard)
        
        agg_factor = self.opponent_aggressiveness

        # === Case A: RAISE ===
        if action.action_type == ActionType.RAISE:
            # Shift the center of the Sigmoid curve.
            # Standard center is 0.7 (Strength > 0.7 implies Raise).
            # If Agg < 1.0 (Passive), Center shifts UP (e.g., to 0.85).
            # If Agg > 1.0 (Aggressive), Center shifts DOWN (e.g., to 0.55).
            
            center_shift = (1.0 - agg_factor) * 0.25
            center = 0.7 + center_shift
            
            # Clamp center to maintain sanity [0.5, 0.95]
            center = max(0.5, min(0.95, center))
            
            # Steepness (k): How decisive is the boundary?
            k = 12 

            # Calculate base probability via Sigmoid
            # P(Raise) = 1 / (1 + e^(-k * (x - center)))
            base_prob = 1 / (1 + math.exp(-k * (strength - center)))
            
            # Bluff adjustment: Aggressive players bluff more frequently
            scaled_bluff = bluff_prob * agg_factor
            
            return min(0.99, base_prob + scaled_bluff)

        # === Case B: CALL ===
        elif action.action_type == ActionType.CALL:
            # Modeled as a Gaussian Bell Curve centered at medium strength (0.6).
            # Passive players have a wider calling range (larger variance).
            
            # Standard width (variance proxy)
            width = 0.15 
            
            # If Passive (Agg < 1.0), increase width to represent "Calling Station" behavior
            if agg_factor < 1.0:
                width += (1.0 - agg_factor) * 0.2
            
            # Gaussian function: e^(-(x - center)^2 / width)
            return math.exp(-((strength - 0.6) ** 2) / width)

        # === Case C: CHECK ===
        elif action.action_type == ActionType.CHECK:
            # Two possibilities for Checking:
            # 1. Weakness (Standard)
            # 2. Trapping (Monster Hand) - Highly dependent on aggressiveness
            
            # Probability of Trapping (Slowplaying a monster)
            # Passive players trap significantly more often.
            if strength > 0.90:
                base_trap_prob = 0.30
                # If Agg=0.5, trap_prob -> 0.30 + 0.25 = 0.55 (Very high)
                # If Agg=1.5, trap_prob -> 0.30 - 0.25 = 0.05 (Very low)
                trap_modifier = (1.0 - agg_factor) * 0.5
                trap_prob = max(0.01, min(0.9, base_trap_prob + trap_modifier))
                return trap_prob

            # Standard Weak Check (Reverse Sigmoid)
            # Weaker hands check more often.
            return 1 / (1 + math.exp(10 * (strength - 0.4)))

        # === Case D: FOLD ===
        elif action.action_type == ActionType.FOLD:
            # Reverse Sigmoid centered at 0.3.
            # Only very weak hands fold. This is relatively style-independent,
            # though aggressive players might fold marginal hands to re-raise elsewhere.
            return 1 / (1 + math.exp(12 * (strength - 0.3)))

        return 0.5

    def _get_preflop_strength(self, hand_str: str) -> float:
        # Simplified strength map for Likelihood calculation
        if hand_str in ["AA", "KK", "QQ", "AKs"]: return 0.95
        if hand_str in ["JJ", "TT", "AKo", "AQs", "KQs"]: return 0.85
        if hand_str[0] == hand_str[1]: return 0.7 
        if "A" in hand_str: return 0.6 # Ax is strong in HU
        if hand_str.endswith('s') and hand_str[0] in "TJQKA" and hand_str[1] in "TJQKA": return 0.55
        return 0.2

    def _get_postflop_strength(self, hand_str: str, board_treys: List[int]) -> float:
        rank1, rank2 = hand_str[0], hand_str[1]
        is_suited = hand_str.endswith('s')
        is_pair = (rank1 == rank2)
        suits = ['s', 'h', 'd', 'c']
        candidates = []

        if is_pair:
            for s1, s2 in itertools.combinations(suits, 2):
                candidates.append([TreysCard.new(rank1 + s1), TreysCard.new(rank2 + s2)])
        elif is_suited:
            for s in suits:
                candidates.append([TreysCard.new(rank1 + s), TreysCard.new(rank2 + s)])
        else:
            for s1 in suits:
                for s2 in suits:
                    if s1 == s2: continue
                    candidates.append([TreysCard.new(rank1 + s1), TreysCard.new(rank2 + s2)])

        valid_hand = None
        for hand_combo in candidates:
            if hand_combo[0] not in board_treys and hand_combo[1] not in board_treys:
                valid_hand = hand_combo
                break
        
        if valid_hand is None: return 0.0
        score = self.evaluator.evaluate(board_treys, valid_hand)
        # Normalize: 0 (worst) to 1 (best)
        return 1.0 - (score / 7462.0)

    def _display_top_beliefs(self, top_n=5):
        sorted_belief = sorted(self.opponent_belief.items(), key=lambda x: x[1], reverse=True)
        print(f"[Bayes] Top {top_n} opponent ranges:")
        count = 0
        for hand, prob in sorted_belief:
            if prob < 0.001: break 
            print(f"      {hand}: {prob:.1%}")
            count += 1
            if count >= top_n: break

    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        print(f"\n[Bayes] Inference running...")
        self._display_top_beliefs()

        iterations = 50 if not board else 100
        equity = self.brain.calculate_equity_vs_range(
            self.hand, self.opponent_belief, board, iterations
        )

        print(f"   Hand: {self.hand}, Board: {board}")
        print(f"   Vs Range Equity: {equity:.1%}")
        
        to_call = current_bet - self.current_round_bet
        final_pot = pot + to_call + to_call
        pot_odds = to_call / final_pot if final_pot > 0 else 0
        print(f"   Pot Odds: {pot_odds:.1%}")

        # OPTIMIZATION 2: Mixed Strategy (Anti-Exploitation)
        
        if to_call == 0:
            # Value Bet
            if equity > 0.8:
                # Trap: 15% chance to check huge hands
                if random.random() < 0.15:
                    print("   [Strategy] Trapping with monster hand.")
                    return Action(ActionType.CHECK)
                
                bet_amount = int(pot * 1.0)
                return self._make_raise(bet_amount, min_raise)
            
            # Thin Value Bet / Protection
            elif equity > 0.60:
                bet_amount = int(pot * 0.60)
                return self._make_raise(bet_amount, min_raise)
            
            # Bluff Check-Raise (Simulated by betting if checked to)
            # If we are weak but want to steal
            elif equity < 0.4 and random.random() < 0.05:
                print("   [Strategy] Bluffing with weak hand.")
                bet_amount = int(pot * 0.5)
                return self._make_raise(bet_amount, min_raise)
                
            return Action(ActionType.CHECK)
        else:
            call_threshold = pot_odds
            
            # Adjust for bluff probability
            if self._calculate_bluff_probability() > 0.25:
                print("   [Strategy] High bluff probability detected. Widening call range.")
                call_threshold *= 0.8 

            # Raise (Value)
            if equity > 0.75:
                # Trap: 10% chance to just call with monster
                if random.random() < 0.10:
                    print("   [Strategy] Trapping (Just Call) with monster hand.")
                    return Action(ActionType.CALL)
                    
                print("   [Decision] Strong equity. Raising.")
                raise_amount = int((pot + current_bet) * 1.5)
                return self._make_raise(raise_amount, min_raise)

            # Call
            if equity >= call_threshold:
                return Action(ActionType.CALL)
            else:
                # Bluff Raise (Re-raise bluff) - risky but needed in HU
                # Only do this if pot odds aren't terrible (not facing all-in)
                if pot_odds < 0.4 and random.random() < 0.05:
                    print("   [Strategy] Bluff Re-raising!")
                    raise_amount = int((pot + current_bet) * 1.5)
                    return self._make_raise(raise_amount, min_raise)
                    
                print(f"   [Decision] Fold ({equity:.1%} < {call_threshold:.1%}).")
                return Action(ActionType.FOLD)

    def _make_raise(self, amount: int, min_raise: int) -> Action:
        actual_amount = max(amount, min_raise)
        total_commitment = actual_amount + self.current_round_bet
        if total_commitment >= self.stack + self.current_round_bet:
            print("   [Decision] ALL IN")
            return Action(ActionType.ALL_IN)
        return Action(ActionType.RAISE, amount=total_commitment)