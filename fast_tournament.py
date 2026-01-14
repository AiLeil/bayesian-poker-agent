import torch
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time
from concurrent.futures import ProcessPoolExecutor

# Import Game Engine and Agents
from poker_engine.game import Game
from poker_ai.agent import BayesianAgent
from poker_ai.rl_agent import RLAgent
from poker_ai.baseline_agent import BaselineAgent

# === Configuration ===
MATCHES_PER_PAIR = 500   
INITIAL_STACK = 2000     # 100 BB Deep Stack
MAX_WORKERS = os.cpu_count() or 4 

# 主角
HERO = 'Bayes'
# 反派和陪练
VILLAINS = ['Baseline', 'LAG', 'TAG', 'LP', 'TP']

# === Context Manager: Suppress Stdout ===
class SuppressPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# === Helper: Agent Factory ===
def load_agent(name, player_id, stack):
    if name == 'Bayes':
        return BayesianAgent(id=player_id, name="Bayes", stack=stack)
    elif name == 'Baseline':
        return BaselineAgent(id=player_id, name="Baseline", stack=stack)
    else:
        agent = RLAgent(id=player_id, name=name, stack=stack, style=name)
        try:
            model_path = os.path.join("models", f"{name}.pth")
            agent.policy_net.load_state_dict(torch.load(model_path))
            agent.policy_net.eval()
            agent.epsilon = 0.05 
        except:
            pass 
        return agent

# === Core Task: Single Match Execution ===
def play_single_match(args):
    agent_1_name, agent_2_name, stack_size = args
    
    p1 = load_agent(agent_1_name, 0, stack_size)
    p2 = load_agent(agent_2_name, 1, stack_size)
    
    game = Game(small_blind=10, big_blind=20)
    game.add_player(p1)
    game.add_player(p2)
    
    hand_count = 0
    with SuppressPrints():
        while p1.stack > 0 and p2.stack > 0 and hand_count < 400:
            game.start_hand()
            hand_count += 1
            
    if p1.stack > p2.stack:
        return 1 # P1 (Hero) wins
    elif p2.stack > p1.stack:
        return 2 # P2 (Villain) wins
    else:
        return 0 

# === Main Entry Point ===
def run_tournament():
    print(f"=== Bayes vs The World (Challenge Mode) ===")
    print(f"Hero: {HERO}")
    print(f"Villains: {VILLAINS}")
    print(f"Matches per Duel: {MATCHES_PER_PAIR} | Stack: {INITIAL_STACK}")
    print("-" * 60)
    
    total_start_time = time.time()
    
    # 存储结果用于绘图
    results_summary = {}

    # 只生成 Bayes vs Others 的对局列表
    for idx, villain in enumerate(VILLAINS):
        print(f"[{idx+1}/{len(VILLAINS)}] ⚔️ {HERO} vs {villain} ... ", end="", flush=True)
        start_time = time.time()
        
        # 任务列表
        tasks = [(HERO, villain, INITIAL_STACK) for _ in range(MATCHES_PER_PAIR)]
        
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            outcomes = list(executor.map(play_single_match, tasks))
            
        hero_wins = outcomes.count(1)
        win_rate = hero_wins / MATCHES_PER_PAIR
        
        results_summary[villain] = win_rate
        
        elapsed = time.time() - start_time
        print(f"Time: {elapsed:.1f}s | Win Rate: {win_rate:.1%}")

    print(f"\nTotal Time: {(time.time() - total_start_time)/60:.1f} mins")
    
    # 绘制更直观的柱状图，而不是热力图
    plot_performance_bar(results_summary)

def plot_performance_bar(results):
    villains = list(results.keys())
    win_rates = [results[v] * 100 for v in villains]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 定义颜色：赢 Baseline 是高光时刻，用金色/橙色，其他用蓝色
    colors = ['#FFD700' if v == 'Baseline' else '#4682B4' for v in villains]
    
    bars = ax.bar(villains, win_rates, color=colors, edgecolor='black', alpha=0.8)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 50% 基准线
    ax.axhline(y=50, color='red', linestyle='--', linewidth=2, label='Break-even (50%)')
    
    ax.set_ylabel('Win Rate (%)', fontsize=12)
    ax.set_title(f'{HERO} Performance Analysis (vs Different Styles)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig("bayes_performance.png")
    print("\n[Output] Performance chart saved as 'bayes_performance.png'")
    plt.show()

if __name__ == "__main__":
    run_tournament()