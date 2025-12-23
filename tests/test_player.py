import pytest
from poker_engine.player import Player, PlayerState

def test_player_initialization():
    p = Player("Hero", 100.0)
    assert p.name == "Hero"
    assert p.stack == 100.0
    assert p.state == PlayerState.ACTIVE
    assert p.hand == []

def test_player_bet_normal():
    p = Player("Hero", 100.0)
    amount = p.bet(30.0)
    
    assert amount == 30.0
    assert p.stack == 70.0
    assert p.current_bet == 30.0
    assert p.state == PlayerState.ACTIVE

def test_player_bet_all_in():
    p = Player("Hero", 50.0)
    # 只有50，想下注100
    amount = p.bet(100.0)
    
    # 应该自动All-in，只下注50
    assert amount == 50.0
    assert p.stack == 0
    assert p.state == PlayerState.ALL_IN

def test_player_fold():
    p = Player("Hero", 100.0)
    p.fold()
    assert p.state == PlayerState.FOLDED

def test_negative_bet():
    p = Player("Hero", 100.0)
    with pytest.raises(ValueError):
        p.bet(-10)