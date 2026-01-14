from typing import List, Dict
import random
from treys import Card as TreysCard
from treys import Evaluator
from poker_engine.card import Card

# 注意：这里千万不要写 'from poker_ai.equity import ...'

class EquityCalculator:
    def __init__(self):
        self.evaluator = Evaluator()
        # Pre-generate a list of 52 integers in Treys format to ensure consistent IDs
        self.FULL_DECK_TREYS = self._generate_full_treys_deck()

    def _generate_full_treys_deck(self) -> List[int]:
        """
        Generates a list of integers for all 52 cards recognized by Treys.
        Fully matches our Card class rank/suit definitions.
        """
        ranks = '23456789TJQKA'
        suits = 'shdc'
        deck = []
        for r in ranks:
            for s in suits:
                # Ensure the int generated here matches exactly what calculate_equity uses
                deck.append(TreysCard.new(f"{r}{s}"))
        return deck

    def calculate_equity(self, hero_hand: List[Card], board: List[Card], iterations: int = 100) -> float:
        """
        Calculates hand equity (win probability).
        Uses Set Difference to completely solve the KeyError caused by duplicate cards.
        """
        # 1. Convert known cards
        try:
            hero_hand_treys = [TreysCard.new(str(c)) for c in hero_hand]
            board_treys = [TreysCard.new(str(c)) for c in board]
        except Exception:
            # If conversion fails (e.g., illegal card), return default equity to prevent training crash
            return 0.5

        # 2. Use set subtraction to get the remaining deck (Unknown Cards)
        known_set = set(hero_hand_treys + board_treys)
        full_set = set(self.FULL_DECK_TREYS)
        
        # Remaining cards = Full Deck - Known Cards
        unknown_cards = list(full_set - known_set)

        # Safety check: Return if not enough cards to simulate
        cards_needed_for_board = 5 - len(board_treys)
        total_draw_needed = 2 + cards_needed_for_board # 2 for Villain + Board Runout

        if len(unknown_cards) < total_draw_needed:
            return 0.5

        wins = 0
        
        # 3. Monte Carlo Simulation
        for _ in range(iterations):
            try:
                # Draw from the remaining deck
                drawn_cards = random.sample(unknown_cards, total_draw_needed)
                
                villain_hand_treys = drawn_cards[:2]
                runout_board = drawn_cards[2:]
                
                final_board = board_treys + runout_board
                
                # Double check for duplicates (Theoretically impossible with set logic, but good for Treys safety)
                # eval_cards = final_board + hero_hand_treys
                # if len(set(eval_cards)) != len(eval_cards): continue

                hero_score = self.evaluator.evaluate(final_board, hero_hand_treys)
                villain_score = self.evaluator.evaluate(final_board, villain_hand_treys)

                if hero_score < villain_score: 
                    wins += 1
                elif hero_score == villain_score:
                    wins += 0.5
            except KeyError:
                # In the extremely rare case Treys crashes, skip this simulation to keep the program alive
                continue
            except Exception:
                continue

        return wins / iterations if iterations > 0 else 0.5

    def calculate_equity_vs_range(self, hero_hand: List[Card], villain_range: Dict[str, float], board: List[Card], iterations: int = 100) -> float:
        """
        Calculates equity against a specific range (for Bayesian Agent).
        """
        hero_hand_treys = [TreysCard.new(str(c)) for c in hero_hand]
        board_treys = [TreysCard.new(str(c)) for c in board]
        
        known_cards_base = set(hero_hand_treys + board_treys)
        
        # Filter valid range combos
        valid_range_combos = []
        weights = []
        
        for hand_str, prob in villain_range.items():
            if prob < 0.001: continue
            try:
                # Get all combos for this range string
                combos = self._range_str_to_combos(hand_str, list(known_cards_base))
                for combo in combos:
                    valid_range_combos.append(combo)
                    weights.append(prob)
            except:
                continue

        if not valid_range_combos:
            return 0.5

        wins = 0
        
        # Pre-calculate full set to avoid repeated creation in loop
        full_set = set(self.FULL_DECK_TREYS)

        for _ in range(iterations):
            try:
                # 1. Randomly select opponent hand based on weights
                villain_hand_treys = random.choices(valid_range_combos, weights=weights, k=1)[0]
                
                # 2. Build simulation deck for this iteration
                # Exclude: Hero hand + Board + Villain's selected hand
                current_known = known_cards_base.union(set(villain_hand_treys))
                
                simulation_deck = list(full_set - current_known)
                
                # 3. Deal remaining board cards
                cards_needed = 5 - len(board_treys)
                if cards_needed > 0:
                    if len(simulation_deck) < cards_needed: continue
                    runout = random.sample(simulation_deck, cards_needed)
                    final_board = board_treys + runout
                else:
                    final_board = board_treys

                # 4. Evaluate
                hero_score = self.evaluator.evaluate(final_board, hero_hand_treys)
                villain_score = self.evaluator.evaluate(final_board, villain_hand_treys)

                if hero_score < villain_score:
                    wins += 1
                elif hero_score == villain_score:
                    wins += 0.5
            except:
                continue

        return wins / iterations

    def _range_str_to_combos(self, hand_str: str, known_cards: List[int]) -> List[List[int]]:
        rank1, rank2 = hand_str[0], hand_str[1]
        is_suited = hand_str.endswith('s')
        is_pair = (rank1 == rank2)
        
        combos = []
        suits = ['s', 'h', 'd', 'c']
        
        # Helper: Create Treys card quickly
        def make_card(r, s): return TreysCard.new(f"{r}{s}")

        if is_pair:
            import itertools
            for s1, s2 in itertools.combinations(suits, 2):
                c1, c2 = make_card(rank1, s1), make_card(rank2, s2)
                if c1 not in known_cards and c2 not in known_cards:
                    combos.append([c1, c2])
        elif is_suited:
            for s in suits:
                c1, c2 = make_card(rank1, s), make_card(rank2, s)
                if c1 not in known_cards and c2 not in known_cards:
                    combos.append([c1, c2])
        else:
            # Offsuit
            for s1 in suits:
                for s2 in suits:
                    if s1 == s2: continue
                    c1, c2 = make_card(rank1, s1), make_card(rank2, s2)
                    if c1 not in known_cards and c2 not in known_cards:
                        combos.append([c1, c2])
        return combos