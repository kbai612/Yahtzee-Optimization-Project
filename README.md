# Yahtzee Strategy Simulation – ISYE 6644

This project simulates games of Yahtzee using several strategies to evaluate their performance via Monte Carlo simulation. The objective is to determine which strategy scores highest on average over many games.

---

## How to Run

1. **Run all strategy simulations:**
```bash
python yahtzee_simulator.py
```

2. **Generate statistical plots and summary metrics:** Open and run all cells in:
```bash
analysis/analysis.ipynb
```

3. **Perform head-to-head strategy comparison:** Open and run all cells in: 
```bash
analysis/head_to_head.ipynb
```

Results and plots will be saved to `results/` and `plots/` directories, which are auto-created.

---

## File Descriptions

### Core Simulation Files
- **`yahtzee_simulator.py`**: Main script for running simulations across all strategies. Computes average scores, saves results to CSV.
- **`scoreboard.py`**: Scoring rules for each Yahtzee category.
- **`dice_rolling.py`**: Manages dice rolling and rerolling logic.

### Strategy Modules (in `strategies/` folder)
- **`multiples_strategy.py`**: Always picks the category with the highest score after each roll.
- **`multiples_plus_strategy.py`**: Always picks the category with the highest score after each roll with added zero out logic
- **`upper_focus_strategy.py`**: Focuses on maximizing upper section scores (1s-6s) to earn the 35-point bonus.
- **`yahtzee_focus_strategy.py`**: Aggressively targets Yahtzee rolls even at the expense of consistency.
- **`tunnel_vision_strategy.py`**: Dynamically chooses a strategy based on the initial roll each turn.

### Analysis & Evaluation
- **`analysis.ipynb`**: Jupyter notebook to compute summary statistics (mean, median, standard deviation, confidence intervals) and generate histograms and a boxplot for all strategies.
- **`head_to_head.ipynb`**: Jupyter notebook that simulates head-to-head comparisons between strategies, saves win rate matrix, and plots a heatmap.

### Outputs
- **`results/`**: Stores CSV files with raw scores, summary stats, and head-to-head win matrix.
- **`plots/`**: Stores visualizations such as histograms, boxplots, and heatmaps.


## Requirements
- Python 3.x
- Packages: `numpy`, `pandas`, `matplotlib`

Install dependencies via pip:
```bash
pip install numpy pandas matplotlib
```
To launch Jupyter: 
```bash
jupyter notebook
```
---

## Authors
Kevin Bai, James Lawinger  
ISYE 6644 - Group 44  
Spring 2025

---

## References
- https://pi.math.cornell.edu/~mec/2006-2007/Probability/Yahtzee.htm
- https://en.wikipedia.org/wiki/Yahtzee
- https://solitaired.com/guides/yahtzee-strategy
- https://www.dumbthoughtsthatmakemelaugh.com/blog/yahtzee-strategy
- http://www.yahtzee.org.uk/strategy.html
- https://chat.openai.com/ (Used for code refinement and documentation)

