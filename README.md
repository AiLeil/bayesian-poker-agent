# Bayesian Poker Agent (BPA)

<p align="center">
    <b>English</b> | <a href="./README_zh.md">简体中文</a>
</p>


This project implements an advanced **Bayesian Inference Agent** for Heads-Up No-Limit Texas Hold'em, designed to master imperfect information games through dynamic opponent modeling. Unlike "Black Box" Deep RL methods that require millions of hands to converge, the **Bayesian Agent** leverages probabilistic graphical models to update beliefs about the opponent's hand range in real-time, allowing for rapid adaptation and exploitation.

To rigorously evaluate the agent's performance, we constructed a diverse competitive arena featuring five distinct opponent archetypes:

* **Baseline Agent:** A strong, heuristic-based opponent playing solid "ABC Poker" driven by Monte Carlo equity calculations.
* **Deep RL Agents (DQN):** Four specialized neural network agents trained with reward shaping to mimic classic human playstyles:
    * **LAG (Loose-Aggressive):** Plays wide ranges and bets frequently.
    * **TAG (Tight-Aggressive):** Selective with hands but aggressive when entering pots.
    * **LP (Loose-Passive):** "Calling Station" that rarely folds but rarely raises.
    * **TP (Tight-Passive):** "Rock" style that only plays premium hands passively.

### Benchmark Results

In a 2,500-hand deep-stack tournament (500 matches per pair), the Bayesian Agent demonstrated superior dominance across the board, achieving a **74.6% win rate** against the strong Baseline and **>94% win rates** against all specific playstyles.

![Performance Analysis](benchmark_result.png)
*(Figure: Bayesian Agent Win Rates vs. Different Opponent Styles)*