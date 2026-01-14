import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Fill in benchmark/tournament result data here
# ==========================================

# Scenario A: Bayesian win rate vs four styles (from benchmark.py results)
# Example: 45.2% vs LAG, 58.5% vs TAG...
bayes_vs_others = {
    'LAG': 45.2,  # Fill in your real data
    'TAG': 58.5,
    'LP':  82.1,
    'TP':  95.0
}

# Scenario B: Average win rate in round robin (calculate mean from fast_tournament.py)
# This represents "Overall Dominance"
overall_win_rates = {
    'Bayes': 70.2, # (45.2 + 58.5 + 82.1 + 95.0) / 4
    'LAG':   55.0,
    'TAG':   52.0,
    'LP':    38.0,
    'TP':    34.8
}

# ==========================================
# 2. Plotting Logic (No modification needed)
# ==========================================

def plot_radar_chart():
    """
    Plot Radar Chart: Show Bayes adaptability vs different styles
    """
    labels = list(bayes_vs_others.keys())
    stats = list(bayes_vs_others.values())

    # Close the circle
    stats += stats[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Plot lines and fill
    ax.plot(angles, stats, color='#1f77b4', linewidth=2, linestyle='solid')
    ax.fill(angles, stats, color='#1f77b4', alpha=0.25)

    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=12, fontweight='bold')
    
    # Set scale (0% - 100%)
    ax.set_ylim(0, 100)
    plt.yticks([20, 40, 60, 80], ["20%", "40%", "60%", "80%"], color="grey", size=10)
    
    plt.title('Bayesian Agent Performance Profile\n(Win Rate vs. Styles)', size=15, y=1.1)
    
    plt.savefig('viz_radar.png', dpi=300, bbox_inches='tight')
    print("Generated: viz_radar.png")
    plt.show()

def plot_bar_chart():
    """
    Plot Bar Chart: Show overall strength ranking of all Agents
    """
    # Sort
    sorted_data = dict(sorted(overall_win_rates.items(), key=lambda item: item[1], reverse=True))
    agents = list(sorted_data.keys())
    rates = list(sorted_data.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define colors: Highlight Bayes, grey for others
    colors = ['#1f77b4' if 'Bayes' in x else '#a9a9a9' for x in agents]
    
    bars = ax.bar(agents, rates, color=colors, edgecolor='black', alpha=0.8)

    # Add numeric labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add 50% baseline
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Break-even (50%)')

    ax.set_ylabel('Average Win Rate (%)', fontsize=12)
    ax.set_title('Overall Tournament Leaderboard', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend()
    
    plt.savefig('viz_leaderboard.png', dpi=300, bbox_inches='tight')
    print("Generated: viz_leaderboard.png")
    plt.show()

if __name__ == "__main__":
    # Set style
    plt.style.use('ggplot') 
    
    print("=== Generating Visualizations ===")
    plot_radar_chart()
    plot_bar_chart()