from poker_engine.card import Card
from poker_ai.equity import EquityCalculator

def test_equity():
    calc = EquityCalculator()
    
    # Scenario 1: AA vs Random (Pre-flop)
    # AA is the strongest starting hand, equity should be around 85%
    hole = [Card('A', 's'), Card('A', 'h')]
    board = []
    equity = calc.calculate_equity(hole, board, iterations=2000)
    print(f"Hand: AA, Board: None -> Equity: {equity:.2%} (Expected ~85%)")

    # Scenario 2: Flush Draw
    # Hand: Ts, 9s. Board: 2s, 3s, Kh
    # Win if another spade hits. Equity should be around 35%
    hole = [Card('T', 's'), Card('9', 's')]
    board = [Card('2', 's'), Card('3', 's'), Card('K', 'h')]
    equity = calc.calculate_equity(hole, board, iterations=2000)
    print(f"Hand: Ts9s, Board: 2s3sKh -> Equity: {equity:.2%} (Expected ~35%)")
    
    # Scenario 3: Made Hand (Nut/Win)
    # Hand: As Ks, Board: Qs Js Ts (Royal Flush)
    hole = [Card('A', 's'), Card('K', 's')]
    board = [Card('Q', 's'), Card('J', 's'), Card('T', 's')]
    equity = calc.calculate_equity(hole, board, iterations=100)
    print(f"Hand: Royal Flush -> Equity: {equity:.2%} (Expected 100%)")

if __name__ == "__main__":
    test_equity()