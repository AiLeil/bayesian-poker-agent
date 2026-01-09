# tests/test_card.py
import pytest
from poker_engine.card import Card, Deck
from dataclasses import FrozenInstanceError

def test_deck_initialization():
    deck = Deck()
    assert len(deck) == 52
    # 抽查几张牌
    assert isinstance(deck.cards[0], Card)

def test_deck_shuffle():
    deck1 = Deck()
    deck2 = Deck()
    
    # 理论上两副新牌顺序一样
    assert str(deck1.cards) == str(deck2.cards)
    
    deck1.shuffle()
    # 洗牌后大概率顺序不同 (极小概率相同，忽略不计)
    assert str(deck1.cards) != str(deck2.cards)
    # 牌数应当不变
    assert len(deck1) == 52

def test_draw_cards():
    deck = Deck()
    drawn = deck.draw(5)
    
    assert len(drawn) == 5
    assert len(deck) == 47

def test_draw_too_many():
    deck = Deck()
    with pytest.raises(ValueError):
        deck.draw(53)

def test_card_equality():
    """
    [关键测试] 验证 Value Equality (值相等性)。
    以前的普通 class 写法，c1 == c2 会是 False。
    现在的 dataclass 写法，必须是 True。
    """
    c1 = Card('A', 's')
    c2 = Card('A', 's')
    c3 = Card('K', 's')
    
    assert c1 == c2, "两张花色点数相同的牌应该是相等的 (Equality check failed)"
    assert c1 != c3, "不同的牌应该是不等的"

def test_card_immutability():
    """
    [关键测试] 验证 Immutability (不可变性)。
    这是防止后续游戏逻辑意外修改牌面的安全网。
    """
    card = Card('T', 'h')
    
    # 试图修改属性应该抛出异常 (FrozenInstanceError)
    with pytest.raises(FrozenInstanceError):
        card.rank = 'K'
        
    with pytest.raises(FrozenInstanceError):
        card.suit = 'c'

def test_card_hashing():
    """
    [关键测试] 验证可哈希性 (Hashability)。
    只有实现了 __hash__ 的对象才能放进 set() 或作为 dict 的 key。
    这对于后续去重、计算牌力分布非常重要。
    """
    c1 = Card('A', 's')
    c2 = Card('A', 's')
    c3 = Card('K', 'd')
    
    # 将重复的牌放入集合
    card_set = {c1, c2, c3}
    
    # 集合会自动去重，c1 和 c2 应该被视为同一个元素
    assert len(card_set) == 2 
    assert c1 in card_set
    assert c3 in card_set

def test_deck_integrity():
    """
    验证一副新牌是否真的包含 52 张**不重复**的牌。
    """
    deck = Deck()
    unique_cards = set(deck.cards)
    
    # 确保没有重复的牌 (例如没有两张黑桃A)
    assert len(unique_cards) == 52
    
def test_card_to_int():
    """
    验证整数转换逻辑是否符合预期 (rank权重 > suit权重)。
    """
    # 2s (index 0, 0) => 0*4 + 0 = 0
    c_min = Card('2', 's') 
    assert c_min.to_int() == 0
    
    # As (index 12, 0) => 12*4 + 0 = 48
    c_max_rank = Card('A', 's')
    assert c_max_rank.to_int() == 48
    
    # Ac (index 12, 3) => 12*4 + 3 = 51
    c_max = Card('A', 'c')
    assert c_max.to_int() == 51