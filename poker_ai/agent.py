from dataclasses import dataclass
from typing import List
from poker_engine.player import Player
from poker_engine.action import Action, ActionType
from poker_engine.card import Card
from poker_ai.equity import EquityCalculator

@dataclass
class AutoAgent(Player):
    """
    智能体 V1: 基于胜率和赔率做决策
    """
    def __post_init__(self):
        # 初始化大脑
        self.brain = EquityCalculator()

    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        to_call = current_bet - self.current_round_bet
        
        # 1. 思考时间 (算胜率)
        # 翻牌前(Preflop)模拟少一点为了快，翻牌后多模拟一点为了准
        iterations = 500 if not board else 2000
        equity = self.brain.calculate_equity(self.hand, board, iterations)
        
        print(f"\n>> 🤖 {self.name} (AI) 正在思考...")
        print(f"   Hand: {self.hand}, Board: {board}")
        print(f"   Win Rate (Equity): {equity:.1%}")

        # 2. 场景一：没人下注 (Check or Bet?)
        if to_call == 0:
            # 如果胜率很高 (>70%)，尝试价值下注 (Value Bet)
            if equity > 0.7:
                # 下注 1/2 底池
                bet_amount = max(min_raise, int(pot * 0.5))
                # 即使没钱了，也不能下超过 stack
                bet_amount = min(bet_amount, self.stack)
                if bet_amount > 0:
                    print(f"   🤖 牌力强，决定加注!")
                    return Action(ActionType.RAISE, amount=bet_amount + self.current_round_bet)
            
            # 否则安全过牌
            return Action(ActionType.CHECK)

        # 3. 场景二：有人下注 (Fold or Call?)
        # 计算赔率 Pot Odds
        # 赔率 = 我要出的钱 / (底池里已有的钱 + 对手刚下的钱 + 我要出的钱)
        # 这里的 pot 参数还没包含对手这轮刚下的注吗？
        # 在 game.py 的逻辑里，current_bet 包含了对手的下注，但还没进 pot。
        # 所以总回报 = pot (前几轮的) + current_bet * 人数 (粗略估计) + 盲注
        # 简单估算：Total Pot after call = pot + to_call + (对手在这轮的下注，已在 current_bet 里)
        
        # 简化版赔率计算：
        # 假设底池目前显示的是 collected pot。
        # 实际总底池 ≈ pot + (current_bet * 2) 
        final_pot_size = pot + to_call + to_call # 假设对手下注量和我跟注量差不多
        if final_pot_size == 0: pot_odds = 0
        else: pot_odds = to_call / final_pot_size

        print(f"   Pot Odds: {pot_odds:.1%} (需要胜率 > {pot_odds:.1%} 才能回本)")

        # 决策阈值 (加一点 0.05 的保守 buffer，或者激进一点)
        if equity >= pot_odds:
            print(f"   🤖 胜率足够，跟注!")
            return Action(ActionType.CALL)
        else:
            print(f"   🤖 胜率不足，弃牌...")
            return Action(ActionType.FOLD)