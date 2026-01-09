from enum import Enum, auto
from typing import List
from poker_engine.card import Card, Deck
from poker_engine.player import Player, PlayerState
from poker_engine.action import ActionType
from poker_engine.evaluator import Ranker

# ==========================================
# Enums (游戏阶段)
# ==========================================
class GameState(Enum):
    IDLE = auto()      # 游戏未开始
    PREFLOP = auto()   # 翻牌前 (发手牌)
    FLOP = auto()      # 翻牌圈 (3张公牌)
    TURN = auto()      # 转牌圈 (1张公牌)
    RIVER = auto()     # 河牌圈 (1张公牌)
    SHOWDOWN = auto()  # 摊牌结算

# ==========================================
# Game Class
# ==========================================
class Game:
    def __init__(self, small_blind: int = 1, big_blind: int = 2):
        self.players: List[Player] = []
        self.deck = Deck()
        self.board: List[Card] = []  # 公共牌 (最多5张)
        self.pot: int = 0            # 底池总金额 (整数!)
        self.state = GameState.IDLE
        self.dealer_pos: int = 0     # 庄家(Button)的位置索引
        self.evaluator = Ranker()

        # 新增配置
        self.small_blind = small_blind
        self.big_blind = big_blind

    def add_player(self, player: Player):
        """
        让玩家加入游戏
        """
        self.players.append(player)

    def start_hand(self):
        """
        开始一手新牌局的主流程。
        """
        # 1. 准备工作
        self._reset_state()
        self.deck.shuffle()
        
        # 2. 只有活着的玩家才能参与 (stack > 0)
        active_players = [p for p in self.players if p.stack > 0]
        if len(active_players) < 2:
            print("人数不足，无法开始游戏")
            return

        print(f"\n=== New Hand Started (Dealer: {self.players[self.dealer_pos].name}) ===")
        
        # === 新增：下盲注 ===
        self._post_blinds()
        
        # 3. 发手牌 (Preflop)
        self.state = GameState.PREFLOP
        self._deal_hole_cards()
        print(f"State: {self.state.name}, Pot: {self.pot}")
        
        # Preflop 下注圈
        self._run_betting_round()  

        # 4. 发翻牌 (Flop)
        self.state = GameState.FLOP
        self._deal_community_cards(3)
        print(f"State: {self.state.name}, Board: {self.board}")
        
        # TODO: 这里应该插入 Flop 下注循环
        self._run_betting_round()  

        # 5. 发转牌 (Turn)
        self.state = GameState.TURN
        self._deal_community_cards(1)
        print(f"State: {self.state.name}, Board: {self.board}")
        self._run_betting_round()  

        # 6. 发河牌 (River)
        self.state = GameState.RIVER
        self._deal_community_cards(1)
        print(f"State: {self.state.name}, Board: {self.board}")
        self._run_betting_round()  

        if self._check_hand_over(): return

        # --- Showdown ---
        self._resolve_showdown()

        # 7. 移动庄家位 (为下一局做准备)
        self._move_button()

    def _check_hand_over(self) -> bool:
        """
        检查游戏是否提前结束 (只剩一个人没弃牌)。
        如果结束了，直接分钱并结束本局。
        """
        # 统计还活着(没Fold且没Out)的人
        active_players = [p for p in self.players if p.state != PlayerState.FOLDED and p.state != PlayerState.OUT]
        
        # 如果只剩 1 个人，他直接赢
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\nEveryone else folded. {winner.name} wins {self.pot}")
            self._payout([winner])
            # 这一局结束，不再发后面的牌
            return True
            
        return False

    def _resolve_showdown(self):
        """
        摊牌阶段：计算所有活着的玩家牌力，决定谁赢。
        """
        self.state = GameState.SHOWDOWN
        print("\n=== SHOWDOWN ===")
        
        # 只计算没弃牌的人
        active_players = [p for p in self.players if p.state != PlayerState.FOLDED and p.state != PlayerState.OUT]
        
        # 1. 计算每个人的分数
        scores = []
        for p in active_players:
            # 调用裁判 (Treys)
            score = self.evaluator.score(p.hand, self.board)
            rank_name = self.evaluator.get_rank_class(score)
            print(f"{p.name}: {p.hand} -> {rank_name} (Score: {score})")
            scores.append((score, p))
        
        # 2. 找到最强分数 (Treys 分数越低越好，1是皇家同花顺)
        if not scores: return
        best_score = min(scores, key=lambda x: x[0])[0]
        
        # 3. 找到赢家 (处理平局 Split Pot)
        winners = [p for score, p in scores if score == best_score]
        
        # 4. 分钱
        self._payout(winners)

    def _payout(self, winners: List[Player]):
        """
        分钱逻辑。
        """
        if not winners:
            return

        # 平分底池
        prize = self.pot // len(winners)
        extra = self.pot % len(winners)

        print(f"\n$$$ Payout $$$ Pot: {self.pot}")
        for p in winners:
            p.stack += prize
            print(f"{p.name} wins {prize}!")
        
        # 零头给第一位
        if extra > 0:
            winners[0].stack += extra
            print(f"{winners[0].name} gets extra {extra} dust.")

        self.pot = 0

    def _reset_state(self):
        """
        重置上一局的残留状态
        """
        self.pot = 0
        self.board = []
        self.deck = Deck() # 拿一副新牌 (或者重新洗牌)
        
        # 重置每个玩家的状态
        for p in self.players:
            p.hand = [] # 清空手牌
            p.current_round_bet = 0
            p.total_pot_contribution = 0
            # 复活有钱的玩家
            if p.stack > 0:
                p.state = PlayerState.ACTIVE
            else:
                p.state = PlayerState.OUT

    def _deal_hole_cards(self):
        """
        给每个在座的 Active 玩家发 2 张底牌
        """
        # 德州扑克规则：从庄家左手边第一个人开始发
        # 这里简化处理，直接遍历发
        for p in self.players:
            if p.state == PlayerState.ACTIVE:
                cards = self.deck.draw(2)
                p.receive_cards(cards)

    def _deal_community_cards(self, n: int):
        """
        发公共牌 (Flop=3, Turn=1, River=1)
        """
        # 销牌 (Burn card) - 模拟真实赌场规则，防止作弊
        self.deck.draw(1) 
        
        # 发牌
        new_cards = self.deck.draw(n)
        self.board.extend(new_cards)

    def _move_button(self):
        """
        移动庄家按钮到下一个人
        """
        self.dealer_pos = (self.dealer_pos + 1) % len(self.players)

    def _post_blinds(self):
        """
        强制扣除小盲和大盲注。
        处理 2人局 (Heads-up) vs 多人局 的位置差异。
        """
        n = len(self.players)
        if n < 2:
            return

        # 1. 计算 SB 和 BB 的索引
        if n == 2:
            # 单挑规则：Dealer 是小盲，对手是大盲
            sb_pos = self.dealer_pos
            bb_pos = (self.dealer_pos + 1) % n
        else:
            # 常规规则：Dealer 下家是小盲，下下家是大盲
            sb_pos = (self.dealer_pos + 1) % n
            bb_pos = (self.dealer_pos + 2) % n

        # 2. 强制扣钱 (调用 Player.bet)
        # 注意：这里我们直接用 bet 方法，虽然他们是被迫的
        print(f"--- Posting Blinds (DealerPos: {self.dealer_pos}) ---")
        
        # 小盲
        p_sb = self.players[sb_pos]
        actual_sb = p_sb.bet(self.small_blind)
        print(f"{p_sb.name} posts SB: {actual_sb}")

        # 大盲
        p_bb = self.players[bb_pos]
        actual_bb = p_bb.bet(self.big_blind)
        print(f"{p_bb.name} posts BB: {actual_bb}")

        # 3. 钱进底池
        # 注意：现在钱还在玩家的 current_round_bet 里，
        # 我们暂时不把钱挪进 self.pot，要等这一轮下注结束（Gather Bets）才挪。
        # 但在某些写法里，盲注也可以直接进 pot。为了简单，我们先不动，
        # 因为后续的 Betting Loop 会统一处理“收集筹码”的逻辑。
    
    def _collect_bets(self):
        """
        [荷官动作] 结束一轮下注后，把大家桌前的筹码收进底池。
        """
        round_total = 0
        for p in self.players:
            if p.current_round_bet > 0:
                amount = p.current_round_bet
                self.pot += amount
                round_total += amount
                # 清空玩家这一轮的下注记录，为下一轮做准备
                # 注意：total_pot_contribution 不清空
                p.reset_round_state()
        
        if round_total > 0:
            print(f"--- Collecting Bets: {round_total} added to Pot. Total Pot: {self.pot} ---")
        
    def _run_betting_round(self):
        """
        [核心逻辑] 真正的下注循环 (v1.0)
        """
        # 1. 确定谁先说话
        # Preflop: 大盲下一家 (BB+1) 先说
        # Postflop: 庄家下一家 (SB) 先说
        active_players = [p for p in self.players if p.state != PlayerState.FOLDED and p.state != PlayerState.OUT]
        if len(active_players) <= 1:
            return # 剩一个人直接赢，不用下注

        # 确定起始位置索引
        start_index = (self.dealer_pos + 1) % len(self.players)
        if self.state == GameState.PREFLOP:
            # 翻牌前，大盲(BB)后面那个先说话
            # BB 是 dealer+2 (多人) 或 dealer+1 (HU)
            # 简单起见，我们统一遍历找到 BB 的下家
            # (这里为了简化代码，暂且用 dealer+1 开始遍历，稍后会自动跳过已经下过盲注的人)
            # 更严谨的逻辑是维护一个 current_actor_index
            current_actor_index = (self.dealer_pos + 1) % len(self.players) # SB
            if len(self.players) > 2:
                current_actor_index = (self.dealer_pos + 3) % len(self.players) # UTG
            else:
                current_actor_index = self.dealer_pos # HU: Dealer is SB, acts first
        else:
            current_actor_index = (self.dealer_pos + 1) % len(self.players)

        # 当前轮次的最高下注额 (High Bet)
        current_bet = 0
        for p in self.players:
            current_bet = max(current_bet, p.current_round_bet)
        
        # 最小加注额 (默认为大盲)
        min_raise = current_bet + self.big_blind

        # 记录谁是“最后一个激进者”(Aggressor)。如果轮回到他没人加注，就结束。
        # 初始设为 None，意味着大家要把一圈都表态完
        last_aggressor = None 
        
        # 标记是否所有人都在本轮表过态了 (防止一开始大家都没动就直接结束)
        players_acted_count = 0

        print(f"\n[Betting Round: {self.state.name}] Current Pot: {self.pot}")

        while True:
            # 1. 检查是否只剩一人 (其他人Fold)
            active_count = len([p for p in self.players if p.state != PlayerState.FOLDED and p.state != PlayerState.OUT])
            if active_count <= 1:
                break

            # 2. 获取当前玩家
            player = self.players[current_actor_index]

            # 3. 跳过不需要行动的人
            # - 已弃牌 (FOLDED)
            # - 已输光 (OUT)
            # - 已全押 (ALL_IN) -> 全押的人不需要再做决策，直接跳过
            if player.state in [PlayerState.FOLDED, PlayerState.OUT, PlayerState.ALL_IN]:
                current_actor_index = (current_actor_index + 1) % len(self.players)
                # 如果绕了一圈全是 All-in/Fold，这会死循环吗？需要检测
                # 简单检测：如果 active 且非 all-in 的人数为 0，直接结束
                not_allin_count = len([p for p in self.players if p.state == PlayerState.ACTIVE])
                if not_allin_count == 0:
                    break
                continue

            # 4. 判断循环结束条件
            # 如果每个人都表过态了，且当前玩家出的钱等于 current_bet，
            # 并且他不是那个刚刚 Raise 的人（防止自己 Raise 自己 Call），则结束
            if players_acted_count >= active_count and player.current_round_bet == current_bet:
                if last_aggressor is None or player != last_aggressor:
                    break

            # 5. 询问玩家动作
            # 旧代码: action = player.get_action(current_bet, min_raise)
            # 新代码: 传入 pot 和 board
            action = player.get_action(current_bet, min_raise, self.pot, self.board)
            players_acted_count += 1

            # 6. 处理动作
            if action.action_type == ActionType.FOLD:
                player.fold()
                print(f"{player.name} Folds.")
            
            elif action.action_type == ActionType.CHECK:
                print(f"{player.name} Checks.")
            
            elif action.action_type == ActionType.CALL:
                amount_to_call = current_bet - player.current_round_bet
                player.bet(amount_to_call)
                print(f"{player.name} Calls {amount_to_call}.")

            elif action.action_type == ActionType.RAISE:
                # 加注逻辑
                new_total = action.amount
                added_chips = player.bet(new_total - player.current_round_bet)
                
                # 更新全局状态
                current_bet = new_total
                min_raise = current_bet + (current_bet - (current_bet - added_chips)) # 简化计算，实际应该是上一级 raise 差额
                min_raise = current_bet + self.big_blind # 暂时简化：最小再加一个 BB
                
                last_aggressor = player # 他是新的发起者
                players_acted_count = 1 # 计数器重置！其他人必须重新表态
                print(f"{player.name} Raises to {new_total}.")
            
            elif action.action_type == ActionType.ALL_IN:
                player.bet(player.stack) # 全推
                if player.current_round_bet > current_bet:
                    current_bet = player.current_round_bet
                    last_aggressor = player # All-in 也可以视为一种 Raise
                    players_acted_count = 1
                print(f"{player.name} goes ALL-IN!")

            # 7. 移动到下一个人
            current_actor_index = (current_actor_index + 1) % len(self.players)

        # 循环结束，收钱
        self._collect_bets()