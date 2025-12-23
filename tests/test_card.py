# tests/test_card.py
import pytest
from poker_engine.card import Card, Deck

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