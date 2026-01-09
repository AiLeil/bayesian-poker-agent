from poker_engine.player import Player
from poker_engine.game import Game

def debug_game_flow():
    # 1. 创建游戏引擎
    game = Game()
    
    # 2. 创建两个玩家 (土豪 vs 土豪)
    p1 = Player(name="Alice", stack=1000)
    p2 = Player(name="Bob", stack=1000)
    
    # 3. 加入游戏
    game.add_player(p1)
    game.add_player(p2)
    
    # 4. 开始跑第一局
    game.start_hand()
    
    # 5. 打印结果看看
    print("\n--- Game State Check ---")
    print(f"Alice's Hand: {p1.hand}")
    print(f"Bob's Hand:   {p2.hand}")
    print(f"Board:        {game.board}")
    print(f"Pot:          {game.pot}")

if __name__ == "__main__":
    debug_game_flow()