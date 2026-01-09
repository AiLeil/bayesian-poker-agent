from poker_engine.game import Game
from poker_engine.player import HumanPlayer
from poker_ai.agent import AutoAgent

def start_human_vs_ai():
    # 1. 创建游戏引擎 (小盲1 / 大盲2)
    game = Game(small_blind=1, big_blind=2)
    
    # 2. 创建玩家
    # 👨‍💻 你是人类玩家 (控制台输入)
    human = HumanPlayer(name="Hero(You)", stack=200)
    
    # 🤖 它是 AI 玩家 (自动算胜率)
    bot = AutoAgent(name="Terminator_V1", stack=200)
    
    # 3. 加入游戏
    game.add_player(human)
    game.add_player(bot)
    
    # 4. 开始对战！
    # 我们可以写个死循环让它一直打下去，或者只打一局
    while True:
        # 检查是否有人输光了
        if human.stack <= 0 or bot.stack <= 0:
            print("\nGame Over! 有人破产了。")
            break
            
        input("\n按回车键开始新的一局...")
        game.start_hand()

        # 打印这一局结束后的余额
        print(f"\n--- 💰 Balance Check ---")
        print(f"{human.name}: {human.stack}")
        print(f"{bot.name}:   {bot.stack}")

if __name__ == "__main__":
    start_human_vs_ai()
    