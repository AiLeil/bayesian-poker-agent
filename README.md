# Bayesian Poker Agent (BPA)

<p align="center">
    <b>English</b> | <a href="./README_zh.md">简体中文</a>
</p>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-In%20Progress-orange)

> **One-Liner:** An adaptive Heads-Up No-Limit Hold'em (HUNL) AI agent that leverages Bayesian Inference to model opponent tendencies and dynamically adjusts strategies for maximum exploitation.

## 1. Motivation

Traditional poker AIs (e.g., Libratus, Pluribus) focus on **GTO (Game Theory Optimal)** strategies, which are computationally expensive and difficult to reproduce for individual developers.
The goal of this project is to build a **lightweight, highly adaptive agent** designed to target common human irrationalities and biases through **Exploitative Play**.

### Highlights
* Utilizes `Beta Distribution` to solve the "Cold Start" problem when historical data on an opponent is scarce.
* Implements a custom-built poker physics engine and state machine from scratch, without relying on black-box libraries.
* Integrates the **Kelly Criterion** for bankroll management and includes a PnL (Profit and Loss) backtesting module.

---

## 2. Architecture

The project follows a **Modular Layered Architecture**, strictly decoupling the "Game Physics" from the "Decision Logic".

```text
bayesian-poker-agent/
├── poker_engine/       # [Physics Layer] Handles game rules, no strategy logic
│   ├── card.py         # Basic Data Structures (Card, Deck)
│   ├── game.py         # Finite State Machine (FSM) managing flow from Pre-flop to River
│   └── pot.py          # Complex pot allocation logic (Main Pot / Side Pots)
├── brain/              # [Observation Layer] Handles stats and inference
│   ├── tracker.py      # Tracks opponent actions across different Streets/Positions
│   └── inference.py    # Core Bayesian Inference Engine (Beta Distribution Updates)
├── strategy/           # [Decision Layer] Handles final decision making
│   ├── equity.py       # Monte Carlo Simulation for Win Rate calculation
│   └── decision.py     # Combines Equity + Posterior Probabilities to output Action
├── tests/              # Unit Tests (TDD)
└── main.py             # Entry Point
```

---

## 3. Tech Stack

| Category | Technology | Usage |
| --- | --- | --- |
| **Language** | Python 3.9+ | Core Development |
| **Core Libs** | `numpy` | Matrix operations & efficient data handling |
| **Stats** | `scipy.stats` | Bayesian Distributions (Beta, Normal) |
| **Testing** | `pytest` | Unit Testing & TDD Workflow |
| **Visualization** | `matplotlib` | Training curves & PnL visualization |
| **Utilities** | `treys` | (Optional) Fast hand strength evaluation |

---

## 4. Roadmap

### Sprint 1: The Physics Engine (In Progress)

* [x] Implement `Card` & `Deck` classes.
* [x] Implement `Player` class with stack management.
* [ ] Implement Game Loop (State Machine transitions).
* [ ] Basic CLI for Random Bot vs. Random Bot.

### Sprint 2: The Bayesian Brain

* [ ] Design `OpponentModel` class.
* [ ] Implement Bayesian Update mechanism.
* [ ] Visualize belief convergence (Beta Distribution plots).

### Sprint 3: Strategy & Exploitation

* [ ] Implement Monte Carlo Equity Calculator.
* [ ] Logic for "Bluffing" vs. "Value Betting" based on opponent stats.
* [ ] Backtesting framework against static strategies (e.g., Calling Station).

---

## 5. Usage

### Installation

```bash
# 1. Clone the repository
git clone git clone https://github.com/AiLeil/bayesian-poker-agent.git
cd bayesian-poker-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run Tests

This project strictly follows TDD (Test-Driven Development). Run the following to verify:

```bash
python -m pytest
```

### Start Game (Preview)

```bash
python main.py
```

---



*Acknowledgement: Developed with the assistance of Gemini 3 Pro (AI Pair Programmer).*



