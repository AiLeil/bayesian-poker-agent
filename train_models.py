import torch
import os
import sys

# Import Engine
from poker_engine.game import Game
from poker_engine.player import Player
from poker_ai.rl_agent import RLAgent
from poker_ai.baseline_agent import BaselineAgent

# Configuration
TRAIN_EPISODES = 2000 # Number of hands per training round
STACK_SIZE = 2000     # Deep Stack Training
STYLES = ['LAG', 'TAG', 'LP', 'TP']

class SuppressPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def train_style(style_name):
    print(f"\n--- Training Model: {style_name} ---")
    
    # 1. Trainee (The RL Agent we are training)
    # Important: Reset stack in loop, but keep memory across hands
    trainee = RLAgent(id=0, name=f"Agent_{style_name}", stack=STACK_SIZE, style=style_name)
    
    # 2. Opponent (Baseline Agent - The Teacher)
    # Baseline is strong, so RL learns from a tough opponent
    opponent = BaselineAgent(id=1, name="Baseline_Sparring", stack=STACK_SIZE)
    
    game = Game(small_blind=10, big_blind=20)
    game.add_player(trainee)
    game.add_player(opponent)
    
    # Ensure models directory exists
    if not os.path.exists("models"):
        os.makedirs("models")

    # Training Loop
    for episode in range(1, TRAIN_EPISODES + 1):
        # Reset stacks every hand to simulate cash game / tournament reset
        # This prevents one agent from going bust and stopping training
        trainee.stack = STACK_SIZE
        opponent.stack = STACK_SIZE
        
        # Record starting stack for reward calculation
        start_stack = trainee.stack
        
        # Play one hand
        with SuppressPrints():
            game.start_hand()
        
        # === CRITICAL: End of Hand Learning ===
        # Calculate net profit/loss
        won_chips = trainee.stack - start_stack
        
        # Tell the agent the hand is over and what the final result was
        trainee.end_hand(won_chips)
        # ======================================

        if episode % 200 == 0:
            print(f"  Hand {episode}/{TRAIN_EPISODES} completed. Epsilon: {trainee.epsilon:.3f}")

    # Save Model
    save_path = f"models/{style_name}.pth"
    torch.save(trainee.policy_net.state_dict(), save_path)
    print(f"  Model saved: {save_path}")

if __name__ == "__main__":
    # Clean up old models to prevent confusion
    if os.path.exists("models"):
        for f in os.listdir("models"):
            if f.endswith(".pth"):
                os.remove(os.path.join("models", f))
                
    for style in STYLES:
        train_style(style)