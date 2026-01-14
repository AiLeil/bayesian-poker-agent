from typing import List
from poker_engine.deck import Deck
from poker_engine.card import Card
from poker_engine.player import Player, PlayerState
from poker_engine.action import Action, ActionType

class Game:
    def __init__(self, small_blind: int, big_blind: int):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players: List[Player] = []
        self.deck = Deck()
        self.board: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_idx = 0 

    def add_player(self, player: Player):
        self.players.append(player)

    def start_hand(self):
        """
        Orchestrates a single hand of Texas Hold'em.
        """
        # 1. Reset State
        # === Core Fix: Must reset to a fresh deck, instead of just shuffling remaining cards ===
        self.deck.reset() 
        # ========================================================
        
        self.board = []
        self.pot = 0
        self.current_bet = 0
        
        # Reset player states for the new hand
        for p in self.players:
            p.reset_hand()
            if p.stack > 0:
                p.receive_cards(self.deck.draw(2))
            else:
                p.state = PlayerState.OUT

        # Remove busted players from active logic (though loop handles states)
        active_players_count = sum(1 for p in self.players if p.state != PlayerState.OUT)
        if active_players_count < 2:
            return # Cannot play alone

        # 2. Post Blinds
        sb_amount = self.small_blind
        bb_amount = self.big_blind
        
        n = len(self.players)
        sb_idx = self.dealer_idx % n
        bb_idx = (self.dealer_idx + 1) % n
        
        sb_player = self.players[sb_idx]
        bb_player = self.players[bb_idx]
        
        # Force posts (handle all-in logic inside post_blind)
        sb_player.post_blind(sb_amount)
        bb_player.post_blind(bb_amount)
        
        self.pot += (sb_player.current_round_bet + bb_player.current_round_bet)
        self.current_bet = bb_amount

        # 3. Betting Rounds
        rounds = [
            ("Preflop", 0),
            ("Flop", 3),
            ("Turn", 1),
            ("River", 1)
        ]

        hand_ended_early = False

        for round_name, cards_to_deal in rounds:
            # Deal community cards
            if cards_to_deal > 0:
                self.board.extend(self.deck.draw(cards_to_deal))
            
            # Reset round bets (side pots are implicitly handled by main pot for simplicity)
            for p in self.players:
                p.current_round_bet = 0
            self.current_bet = 0

            # Run Betting Loop
            self._run_betting_round()

            # Check if everyone folded except one
            active_count = sum(1 for p in self.players if not p.folded and p.state != PlayerState.OUT)
            if active_count <= 1:
                hand_ended_early = True
                break
            
            # Check if all active players are All-In
            not_all_in_count = sum(1 for p in self.players if not p.folded and not p.all_in and p.state != PlayerState.OUT)
            if not_all_in_count == 0:
                # Everyone is all-in, just deal the rest of the board
                remaining_cards = 5 - len(self.board)
                if remaining_cards > 0:
                    self.board.extend(self.deck.draw(remaining_cards))
                break

        # 4. Payout
        self._distribute_pot()

        # 5. Bayesian Showdown Analysis (Exploitation Hook)
        if not hand_ended_early:
            for p in self.players:
                if hasattr(p, 'analyze_showdown'):
                    opponents = [op for op in self.players if op.id != p.id]
                    if not opponents: continue
                    opponent = opponents[0]
                    
                    if not opponent.folded:
                        last_action = "CHECK"
                        if opponent.total_bet_in_hand > self.big_blind * 2: 
                            last_action = "RAISE"
                        elif opponent.total_bet_in_hand > 0:
                            last_action = "CALL"
                        
                        p.analyze_showdown(opponent.hand, self.board, last_action)

        # 6. Rotate Dealer
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        
    def _run_betting_round(self):
        n = len(self.players)
        is_preflop = (len(self.board) == 0)
        
        if is_preflop:
            current_idx = self.dealer_idx 
        else:
            current_idx = (self.dealer_idx + 1) % n 
            
        aggressor_idx = -1 
        players_acted = 0
        
        while True:
            # Check for termination
            active_players = [p for p in self.players if not p.folded and not p.all_in and p.state != PlayerState.OUT]
            if len(active_players) == 0: break 
            if len(active_players) == 1 and aggressor_idx == -1 and players_acted >= len(active_players): break 
            
            # Check if we circled back to aggressor or everyone checked
            if players_acted >= len(active_players) and (current_idx == aggressor_idx or (aggressor_idx == -1 and self.current_bet == 0)):
                unmatched = [p for p in active_players if p.current_round_bet < self.current_bet]
                if not unmatched:
                    break
            
            player = self.players[current_idx]
            
            # Skip if folded or all-in
            if player.folded or player.all_in or player.state == PlayerState.OUT:
                current_idx = (current_idx + 1) % n
                continue
                
            # Get Action
            min_raise = max(self.big_blind, self.current_bet * 2)
            action = player.get_action(self.current_bet, min_raise, self.pot, self.board)
            
            # Execute Action
            if action.action_type == ActionType.FOLD:
                player.folded = True
                player.state = PlayerState.FOLDED
                
            elif action.action_type == ActionType.CHECK:
                if self.current_bet > player.current_round_bet:
                    player.folded = True
                pass
                
            elif action.action_type == ActionType.CALL:
                amount = self.current_bet - player.current_round_bet
                player.post_blind(amount) 
                self.pot += amount
                
            elif action.action_type == ActionType.RAISE:
                amount_added = action.amount - player.current_round_bet
                player.post_blind(amount_added)
                self.pot += amount_added
                self.current_bet = action.amount
                aggressor_idx = current_idx
                
            elif action.action_type == ActionType.ALL_IN:
                amount = player.stack
                player.post_blind(amount)
                self.pot += amount
                if player.current_round_bet > self.current_bet:
                    self.current_bet = player.current_round_bet
                    aggressor_idx = current_idx
            
            # Notify others (for Bayes memory)
            for p in self.players:
                if hasattr(p, 'observe_action'):
                    p.observe_action(player.id, action, self.board)

            players_acted += 1
            current_idx = (current_idx + 1) % n

    def _distribute_pot(self):
        active_players = [p for p in self.players if not p.folded and p.state != PlayerState.OUT]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.pot
        else:
            # Showdown
            from treys import Evaluator, Card as TreysCard
            evaluator = Evaluator()
            board_treys = [TreysCard.new(str(c)) for c in self.board]
            
            best_score = 7463
            winners = []
            
            for p in active_players:
                hand_treys = [TreysCard.new(str(c)) for c in p.hand]
                score = evaluator.evaluate(board_treys, hand_treys)
                if score < best_score:
                    best_score = score
                    winners = [p]
                elif score == best_score:
                    winners.append(p)
            
            share = self.pot // len(winners)
            for w in winners:
                w.stack += share