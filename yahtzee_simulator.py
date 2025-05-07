import numpy as np
import statistics
import csv
import os
from scoreboard import *
from dice_rolling import *
from strategies.multiples_strategy import multiples_strategy
from strategies.multiples_strategy_plus import multiples_strategy_plus
from strategies.upper_focus_strategy import upper_focus_strategy
from strategies.straight_strategy import straight_strategy
from strategies.yahtzee_focus_strategy import yahtzee_focus_strategy
from strategies.tunnel_vision_strategy import tunnel_vision_strategy

import random
from collections import Counter

class YahtzeeSimulator:
    def __init__(self):
        self.hand = YahtzeeHand()
        self.scorer = YahtzeeScorer()
        self.all_categories = [
            'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
            'three_of_a_kind', 'four_of_a_kind', 'full_house',
            'small_straight', 'large_straight', 'yahtzee', 'chance'
        ]
        
    def simulate_game(self, strategy_function):
        # Initialize empty scorecard
        scorecard = {category: None for category in self.all_categories}
        total_score = 0
        
        # Play 13 rounds (one for each category)
        for _ in range(13):
            # First roll
            self.hand.roll_all()
            
            # Strategy decides which dice to keep/reroll and which category to use
            category, final_dice = strategy_function(self.hand.dice, scorecard, self)
            
            # Score the final dice in the chosen category
            score_method = getattr(self.scorer, f"score_{category}")
            score = score_method(final_dice)
            
            # Update scorecard
            scorecard[category] = score
            total_score += score
            
        # Calculate upper section bonus 35 points
        upper_section = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
        upper_total = sum(scorecard[cat] for cat in upper_section if scorecard[cat] is not None)
        if upper_total >= 63:
            total_score += 35  # Upper section bonus
            
        return total_score, scorecard
    
    def run_monte_carlo(self, strategy_function, num_simulations=10000):
        scores = []
        for _ in range(num_simulations):
            total_score, _ = self.simulate_game(strategy_function)
            scores.append(total_score)
            
        return scores

# Ensure results directory exists
RESULTS_DIR = 'results'
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Function to save scores and print summary
def process_strategy_results(strategy_name, strategy_func, simulator, num_simulations=10000):
    print(f"Running {strategy_name}...")
    scores = simulator.run_monte_carlo(strategy_func, num_simulations)
    
    # Calculate summary stats
    summary = {
        'mean_score': round(statistics.mean(scores), 1),
        'median_score': round(statistics.median(scores), 1),
        'min_score': min(scores),
        'max_score': max(scores),
        'std_dev': round(statistics.stdev(scores), 1)
    }
    print(f"{strategy_name} Results:", summary)
    
    # Save raw scores to CSV
    filename = os.path.join(RESULTS_DIR, f"{strategy_name}_scores.csv")
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['score']) # Header
        for score in scores:
            writer.writerow([score])
    print(f"Saved raw scores to {filename}")
    print("-" * 30)

# Define strategies and their names
strategies = {
    "Multiples": multiples_strategy,
    "Multiples+": multiples_strategy_plus,
    "Straights": straight_strategy, 
    "Upper Focus": upper_focus_strategy,
    "Yahtzee Focus": yahtzee_focus_strategy,
    "Tunnel Vision": tunnel_vision_strategy
}

# Running the simluations
simulator = YahtzeeSimulator()
num_sims = 10000 # Set number of simulations

# Run simulations for each strategy
for name, func in strategies.items():
    process_strategy_results(name, func, simulator, num_sims)

print("Simulations complete. Raw scores saved in 'results/' directory.")
