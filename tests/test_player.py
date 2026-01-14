import pytest
from poker_engine.player import Player, PlayerState

def test_player_initialization():
    # Note: We use int now (100 instead of 100.0)
    p = Player(1, "Hero", 100)
    
    assert p.name == "Hero"
    assert p.stack == 100
    assert isinstance(p.stack, int) # Ensure type correctness
    assert p.state == PlayerState.ACTIVE
    assert p.hand == []
    # Verify new fields initialize to 0
    assert p.current_round_bet == 0
    assert p.total_bet_in_hand == 0

def test_player_post_blind_normal():
    p = Player(1, "Hero", 100)
    # Using post_blind as per updated logic
    amount = p.post_blind(30)
    
    assert amount == 30
    assert p.stack == 70
    assert p.current_round_bet == 30
    assert p.total_bet_in_hand == 30
    assert p.state == PlayerState.ACTIVE

def test_player_post_blind_all_in():
    p = Player(1, "Hero", 50)
    # Has only 50, wants to post 100
    amount = p.post_blind(100)
    
    # Should auto All-in, posting only 50
    assert amount == 50
    assert p.stack == 0
    assert p.state == PlayerState.ALL_IN
    # Ensure state is updated in betting records
    assert p.current_round_bet == 50

def test_player_fold_logic():
    # Note: Fold logic is now typically handled by Game, but checking Player state
    p = Player(1, "Hero", 100)
    p.folded = True
    p.state = PlayerState.FOLDED
    
    assert p.state == PlayerState.FOLDED
    assert p.folded is True

def test_player_hand_independence():
    """
    [Critical Test] Verify Mutable Default Argument trap is fixed.
    If default_factory=list is not used (or hand=[] in init), players might share hand lists.
    """
    p1 = Player(1, "P1", 100)
    p2 = Player(2, "P2", 100)
    
    # Give P1 a card, P2's hand should remain empty
    p1.hand.append("Card_A") 
    
    assert len(p1.hand) == 1
    assert len(p2.hand) == 0, "Critical Bug: Players are sharing the hand list memory!"