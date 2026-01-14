import pytest
from poker_engine.card import Card, Deck
from dataclasses import FrozenInstanceError

def test_deck_initialization():
    deck = Deck()
    assert len(deck) == 52
    # Spot check a few cards
    assert isinstance(deck.cards[0], Card)

def test_deck_shuffle():
    deck1 = Deck()
    deck2 = Deck()
    
    # Theoretically, two new decks have the same order
    assert str(deck1.cards) == str(deck2.cards)
    
    deck1.shuffle()
    # After shuffle, order should be different (ignoring infinitesimally small chance of same order)
    assert str(deck1.cards) != str(deck2.cards)
    # Count should remain unchanged
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
    [Critical Test] Verify Value Equality.
    With dataclasses, c1 == c2 should be True if rank/suit match.
    """
    c1 = Card('A', 's')
    c2 = Card('A', 's')
    c3 = Card('K', 's')
    
    assert c1 == c2, "Two cards with same rank/suit should be equal (Equality check failed)"
    assert c1 != c3, "Different cards should not be equal"

def test_card_immutability():
    """
    [Critical Test] Verify Immutability.
    This acts as a safety net against accidental card modification during game logic.
    """
    card = Card('T', 'h')
    
    # Attempting to modify attributes should raise FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        card.rank = 'K'
        
    with pytest.raises(FrozenInstanceError):
        card.suit = 'c'

def test_card_hashing():
    """
    [Critical Test] Verify Hashability.
    Only hashable objects can be put into set() or used as dict keys.
    Crucial for deduplication and calculating hand strength distributions.
    """
    c1 = Card('A', 's')
    c2 = Card('A', 's')
    c3 = Card('K', 'd')
    
    # Put duplicate cards into a set
    card_set = {c1, c2, c3}
    
    # Set should auto-deduplicate; c1 and c2 count as one
    assert len(card_set) == 2 
    assert c1 in card_set
    assert c3 in card_set

def test_deck_integrity():
    """
    Verify a fresh deck contains 52 UNIQUE cards.
    """
    deck = Deck()
    unique_cards = set(deck.cards)
    
    # Ensure no duplicates (e.g., no two Ace of Spades)
    assert len(unique_cards) == 52
    
def test_card_to_int():
    """
    Verify integer conversion logic matches expectations (rank weight > suit weight).
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