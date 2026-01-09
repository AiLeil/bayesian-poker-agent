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
* Real-time **Monte Carlo Simulation** for accurate Equity calculation.

---

## 2. Architecture

The project follows a **Modular Layered Architecture**, strictly decoupling the "Game Physics" from the "Decision Logic".

```text
bayesian-poker-agent/
├── poker_engine/       # [Physics Layer] Handles game rules, no strategy logic
│   ├── card.py         # Basic Data Structures (Card, Deck)
│   ├── player.py       # Player entity & Stack management
│   ├── game.py         # Finite State Machine (FSM) managing flow
│   ├── action.py       # Action protocols & interfaces
│   └── evaluator.py    # Hand strength evaluator (Wrapper around treys)
├── poker_ai/           # [Brain Layer] Logic & Strategy
│   ├── agent.py        # Core Agent (Decision making based on Odds/Equity)
│   └── equity.py       # Monte Carlo Simulation Engine
├── tests/              # Unit Tests (pytest)
├── main_ai.py          # Entry Point (Human vs AI)
└── main_debug.py       # Debug Script

```

---

## 3. Tech Stack

| Category | Technology | Usage |
| --- | --- | --- |
| **Language** | Python 3.9+ | Core Development |
| **Core Libs** | `numpy` | Matrix operations & efficient data handling |
| **Stats** | `scipy.stats` | Bayesian Distributions (Beta, Normal) |
| **Testing** | `pytest` | Unit Testing & TDD Workflow |
| **Utilities** | `treys` | Fast hand strength evaluation |

---

## 4. Roadmap

### Sprint 1: The Physics Engine (Completed ✅)

* [x] Implement `Card` & `Deck` classes.
* [x] Implement `Player` class with stack management.
* [x] Implement Game Loop (State Machine transitions).
* [x] Basic CLI for Human vs. AI.

### Sprint 2: Strategy & Calculation (In Progress 🚧)

* [x] Implement Monte Carlo Equity Calculator.
* [x] Basic Pot Odds decision model.
* [ ] Implement EV-based Aggression logic.

### Sprint 3: The Bayesian Brain (Planned 📅)

* [ ] Design `OpponentModel` class.
* [ ] Implement Bayesian Update mechanism.
* [ ] Dynamic adjustment against Loose/Aggressive opponents.

---

## 5. Usage

### Installation

```bash
# 1. Clone the repository
git clone [https://github.com/AiLeil/bayesian-poker-agent.git](https://github.com/AiLeil/bayesian-poker-agent.git)
cd bayesian-poker-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

```

### Run Tests

This project strictly follows TDD (Test-Driven Development). Run the following to verify:

```bash
python -m pytest

```

### Start Game (Human vs AI)

```bash
python main_ai.py

```

---

*Acknowledgement: Developed with the assistance of Gemini 3 Pro (AI Pair Programmer).*


