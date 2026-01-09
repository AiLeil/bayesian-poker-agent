import pytest
from poker_engine.player import Player, PlayerState

def test_player_initialization():
    # 注意：我们现在只用 int (100 而不是 100.0)
    p = Player("Hero", 100)
    
    assert p.name == "Hero"
    assert p.stack == 100
    assert isinstance(p.stack, int) # 确保类型也是对的
    assert p.state == PlayerState.ACTIVE
    assert p.hand == []
    # 验证新字段初始化为 0
    assert p.current_round_bet == 0
    assert p.total_pot_contribution == 0

def test_player_bet_normal():
    p = Player("Hero", 100)
    amount = p.bet(30)
    
    assert amount == 30
    assert p.stack == 70
    # 注意：这里改名了，从 current_bet 变成了 current_round_bet
    assert p.current_round_bet == 30
    assert p.total_pot_contribution == 30
    assert p.state == PlayerState.ACTIVE

def test_player_bet_all_in():
    p = Player("Hero", 50)
    # 只有50，想下注100
    amount = p.bet(100)
    
    # 应该自动All-in，只下注50
    assert amount == 50
    assert p.stack == 0
    assert p.state == PlayerState.ALL_IN
    # 确保状态也更新到了 bet 记录里
    assert p.current_round_bet == 50

def test_player_fold():
    p = Player("Hero", 100)
    p.fold()
    assert p.state == PlayerState.FOLDED
    # 我们的新逻辑里，fold 会清空手牌，验证一下
    assert p.hand == []

def test_negative_bet():
    p = Player("Hero", 100)
    with pytest.raises(ValueError):
        p.bet(-10)

def test_player_hand_independence():
    """
    [关键测试] 验证 Mutable Default Argument 陷阱是否被修复。
    如果不使用 default_factory=list，两个玩家可能会共享同一副手牌。
    """
    p1 = Player("P1", 100)
    p2 = Player("P2", 100)
    
    # 给 P1 发牌，理论上 P2 的手牌应该还是空的
    p1.hand.append("Card_A") 
    
    assert len(p1.hand) == 1
    assert len(p2.hand) == 0, "严重Bug: 玩家之间共享了手牌列表！请检查 field(default_factory=list)"