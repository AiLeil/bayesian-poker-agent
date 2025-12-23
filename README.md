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



> **项目简介：** 一个基于贝叶斯推断的德州扑克 AI，能在小样本数据下快速学习对手风格，并动态调整策略以实现最大化剥削。

## 1. 项目初衷

传统的扑克 AI（如 Libratus/Pluribus）专注于 GTO（博弈论最优解），计算资源消耗巨大且难以复现。
本项目的目标是构建一个**轻量级、高适应性**的智能体，针对人类玩家常见的非理性行为偏差，利用统计学方法进行**剥削性对战**。

### 关键技术
* 利用 `Beta Distribution` 解决早期对手数据不足的冷启动问题。
* 从零构建 Python 扑克物理引擎，模拟真实牌局状态机，不依赖黑盒库。
* 引入凯利公式进行资金管理，并包含盈亏回测分析模块。

---

## 2. 系统架构

本项目采用**模块化分层设计**，严格解耦“物理规则”与“玩家决策”。

```text
bayesian-poker-agent/
├── poker_engine/       # [物理层] 负责维护游戏规则，无策略逻辑
│   ├── card.py         # 基础数据结构 (Card, Deck)
│   ├── game.py         # 有限状态机，管理翻牌前至河牌的流程
│   └── pot.py          # 复杂的底池分配逻辑 (主底池 / 边池)
├── brain/              # [观察层] 负责观察和统计
│   ├── tracker.py      # 记录对手在不同阶段和位置的动作
│   └── inference.py    # 贝叶斯推断核心 (Beta 分布更新)
├── strategy/           # [决策层] 负责最终决策
│   ├── equity.py       # 蒙特卡洛模拟计算胜率
│   └── decision.py     # 结合胜率与后验概率输出动作
├── tests/              # 单元测试
└── main.py             # 程序入口
```

---

## 3. 技术栈

| 类别 | 技术 | 用途 |
| --- | --- | --- |
| **语言** | Python 3.9+ | 核心开发语言 |
| **核心库** | `numpy` | 矩阵运算，高效数据处理 |
| **统计** | `scipy.stats` | 贝叶斯分布 (Beta, Normal) 计算 |
| **测试** | `pytest` | 单元测试，测试驱动开发流程 |
| **可视化** | `matplotlib` | 训练曲线与盈亏资金曲线可视化 |
| **工具** | `treys` | (可选) 快速手牌牌力评估 |
---

## 4. 开发路线图

### Sprint 1：物理引擎搭建（进行中）

* [x] 实现 Card 与 Deck 类（基础数据结构）。
* [x] 实现 Player 类及筹码管理。
* [ ] 实现游戏主循环（处理状态流转）。
* [ ] 基础命令行界面（两个随机机器人对战）。

### Sprint 2：贝叶斯大脑

* [ ] 设计 OpponentModel 类。
* [ ] 实现贝叶斯更新机制。
* [ ] 信念收敛可视化（Beta 分布图）。

### Sprint 3：策略与剥削

* [ ] 实现蒙特卡洛胜率计算器。
* [ ] 基于对手数据的“诈唬”与“价值下注”逻辑。
* [ ] 针对静态策略（如跟注站）的回测框架。
---

## 5. 使用说明

### 安装

```bash
# 1. 克隆仓库
git clone git clone https://github.com/AiLeil/bayesian-poker-agent.git
cd bayesian-poker-agent

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows 系统使用: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 运行测试

本项目严格遵循测试驱动开发流程，运行以下命令进行测试：

```bash
python -m pytest
```

### 启动游戏（预览）

```bash
python main.py
```

---

声明：由 Gemini 3 Pro 辅助开发
