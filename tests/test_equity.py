from poker_engine.card import Card
from poker_ai.equity import EquityCalculator

def test_equity():
    calc = EquityCalculator()
    
    # 场景 1: AA vs Random (翻牌前)
    # AA 是最强起手牌，胜率应该在 85% 左右
    hole = [Card('A', 's'), Card('A', 'h')]
    board = []
    equity = calc.calculate_equity(hole, board, iterations=2000)
    print(f"Hand: AA, Board: None -> Equity: {equity:.2%} (Expected ~85%)")

    # 场景 2: 听同花 (Flush Draw)
    # 手牌: 黑桃10, 黑桃9. 公共牌: 黑桃2, 黑桃3, 红桃K
    # 再来一张黑桃就赢。胜率应该在 35% 左右
    hole = [Card('T', 's'), Card('9', 's')]
    board = [Card('2', 's'), Card('3', 's'), Card('K', 'h')]
    equity = calc.calculate_equity(hole, board, iterations=2000)
    print(f"Hand: Ts9s, Board: 2s3sKh -> Equity: {equity:.2%} (Expected ~35%)")
    
    # 场景 3: 已经成牌 (必胜)
    # 手牌: As Ks, 公共牌: Qs Js Ts (皇家同花顺)
    hole = [Card('A', 's'), Card('K', 's')]
    board = [Card('Q', 's'), Card('J', 's'), Card('T', 's')]
    equity = calc.calculate_equity(hole, board, iterations=100)
    print(f"Hand: Royal Flush -> Equity: {equity:.2%} (Expected 100%)")

if __name__ == "__main__":
    test_equity()