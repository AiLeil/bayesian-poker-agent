import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class PokerDQN(nn.Module):
    """
    A simple fully connected neural network for Q-Value estimation.
    """
    def __init__(self, input_size=5, output_size=3):
        super(PokerDQN, self).__init__()
        # 3-layer Neural Network: Input -> Hidden(128) -> Hidden(64) -> Output(3)
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)

    def forward(self, x):
        # Use ReLU activation function
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

def state_to_tensor(hand_strength, pot_odds, stack_ratio, street_code, has_pair):
    """
    Converts poker state into a numerical tensor compatible with the neural network.
    
    Input Features:
    1. Hand Strength (0-1): Current Win Rate (Equity)
    2. Pot Odds (0-1): Ratio of call amount to pot size
    3. Stack Ratio (0-1): Remaining chips / Initial chips
    4. Street (0, 0.33, 0.66, 1): Preflop/Flop/Turn/River
    5. Has Pair (0 or 1): Boolean flag for pairs (Simplified feature)
    """
    features = np.array([hand_strength, pot_odds, stack_ratio, street_code, has_pair], dtype=np.float32)
    return torch.FloatTensor(features)