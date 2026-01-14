import random
import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
from collections import deque
from typing import List, Tuple

from poker_engine.player import Player
from poker_engine.action import Action, ActionType
from poker_engine.card import Card
from poker_ai.equity import EquityCalculator
from poker_ai.brain import PokerDQN, state_to_tensor

# Hyperparameters
BATCH_SIZE = 64
GAMMA = 0.99        # Emphasis on future rewards
EPS_START = 0.9     # High initial exploration
EPS_END = 0.05
EPS_DECAY = 10000   # Decay slowly
TARGET_UPDATE = 10  # How often to update Target Network

ACTION_MAP = {0: ActionType.FOLD, 1: ActionType.CALL, 2: ActionType.RAISE}

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

class RLAgent(Player):
    """
    Agent V5: True DQN with Experience Replay & Temporal Difference Learning
    """
    def __init__(self, id, name, stack, style='NORMAL'):
        super().__init__(id, name, stack)
        self.style = style

        # Neural Networks
        self.policy_net = PokerDQN()
        self.target_net = PokerDQN()
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.0005) # Lower LR for stability
        self.memory = ReplayBuffer(100000)
        self.brain = EquityCalculator()

        # Training State
        self.steps_done = 0
        self.epsilon = EPS_START
        
        # Temporal Memory (Used to link s -> s')
        self.last_state = None
        self.last_action = None
        self.last_stack = stack # Used to calculate single-step Reward

    def get_action(self, current_bet: int, min_raise: int, pot: int, board: List[Card]) -> Action:
        # 1. Capture Current State
        current_state = self._get_current_state(current_bet, pot, board)
        
        # 2. Calculate Immediate Reward from Previous Step (Transition Logic)
        if self.last_state is not None:
            # Calculate chip change for this step as reward
            chip_change = self.stack - self.last_stack
            reward = self._calculate_reward(chip_change, self.last_action, False)
            
            # Store Transition: (s, a, r, s', done=False)
            self.memory.push(self.last_state, self.last_action, reward, current_state, False)
            
            # Learn immediately (Online Learning)
            self._optimize_model()

        # 3. Select Action (Epsilon-Greedy)
        action_idx = self._select_action(current_state)
        
        # 4. Update Pointers for next step
        self.last_state = current_state
        self.last_action = action_idx
        self.last_stack = self.stack
        self.steps_done += 1

        # 5. Convert to Engine Action
        return self._idx_to_action(action_idx, current_bet, min_raise, pot)

    def end_hand(self, won_chips: int):
        """
        Called by train_models.py at the end of the hand to close the loop.
        This provides the final reward and the 'done' signal.
        """
        if self.last_state is not None:
            # Final Reward calculation
            reward = self._calculate_reward(won_chips, self.last_action, True)
            
            # Store Terminal Transition: (s, a, r, None, done=True)
            self.memory.push(self.last_state, self.last_action, reward, None, True)
            
            # Learn
            self._optimize_model()

        # Reset pointers for next hand
        self.last_state = None
        self.last_action = None
        
        # Update Target Network periodically
        if self.steps_done % TARGET_UPDATE == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def _select_action(self, state):
        # Decay Epsilon
        self.epsilon = EPS_END + (EPS_START - EPS_END) * \
                        np.exp(-1. * self.steps_done / EPS_DECAY)
        
        if random.random() < self.epsilon:
            return random.randint(0, 2)
        else:
            with torch.no_grad():
                # === FIX: Add unsqueeze(0) to create a batch dimension [1, 5] ===
                # This ensures the output is [1, 3] and .max(1) works correctly
                q_values = self.policy_net(state.unsqueeze(0))
                return q_values.max(1)[1].item()

    def _optimize_model(self):
        if len(self.memory) < BATCH_SIZE:
            return
        
        transitions = self.memory.sample(BATCH_SIZE)
        batch = list(zip(*transitions))

        state_batch = torch.stack(batch[0])
        action_batch = torch.tensor(batch[1]).unsqueeze(1)
        reward_batch = torch.tensor(batch[2], dtype=torch.float32).unsqueeze(1)
        
        # Compute Q(s_t, a)
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch[3])), dtype=torch.bool)
        non_final_next_states = torch.stack([s for s in batch[3] if s is not None])
        
        next_state_values = torch.zeros(BATCH_SIZE)
        with torch.no_grad():
            if len(non_final_next_states) > 0:
                next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0]
            
        # Compute expected Q values (Bellman Equation)
        expected_state_action_values = (next_state_values.unsqueeze(1) * GAMMA) + reward_batch

        # Loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values)

        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

    def _calculate_reward(self, chip_change, action_idx, is_terminal):
        r = chip_change / 100.0
        
        bias = 0.05
        ACT_FOLD, ACT_CALL, ACT_RAISE = 0, 1, 2
        
        if 'T' in self.style and action_idx != ACT_FOLD: r -= bias
        if 'A' in self.style and action_idx == ACT_CALL: r -= bias * 1.5
        if 'P' in self.style and action_idx == ACT_RAISE: r -= bias * 1.5
        if 'L' in self.style and action_idx == ACT_FOLD: r -= bias

        if is_terminal:
            if chip_change > 0: r += 0.5 
            else: r -= 0.1 
            
        return r

    def _get_current_state(self, current_bet, pot, board):
        equity = self.brain.calculate_equity(self.hand, board, iterations=50)
        
        to_call = current_bet - self.current_round_bet
        final_pot = pot + to_call + to_call
        pot_odds = to_call / final_pot if final_pot > 0 else 0
        
        stack_ratio = self.stack / 2000.0
        street_map = {0: 0.0, 3: 0.33, 4: 0.66, 5: 1.0}
        street_code = street_map.get(len(board), 0.0)
        has_pair = 1.0 if len(self.hand) == 2 and self.hand[0].rank == self.hand[1].rank else 0.0
        
        return state_to_tensor(equity, pot_odds, stack_ratio, street_code, has_pair)

    def _idx_to_action(self, idx, current_bet, min_raise, pot):
        action_type = ACTION_MAP[idx]
        if action_type == ActionType.FOLD:
            return Action(ActionType.FOLD)
        elif action_type == ActionType.RAISE:
            amount = max(min_raise, int(pot * 0.75))
            total = amount + self.current_round_bet
            if total >= self.stack + self.current_round_bet:
                return Action(ActionType.ALL_IN)
            return Action(ActionType.RAISE, amount=total)
        else:
            to_call = current_bet - self.current_round_bet
            if to_call == 0: return Action(ActionType.CHECK)
            return Action(ActionType.CALL)