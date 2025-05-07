import random
import numpy as np
from collections import Counter

class YahtzeeHand:
    def __init__(self, seed=None):
        self.dice = [0, 0, 0, 0, 0]
        self.random = random.Random(seed)  # Optional seeding for reproducibility
        
    def roll_all(self):
        self.dice = [self.random.randint(1, 6) for _ in range(5)]
        return self.dice
    
    def reroll(self, positions):
        # Reroll specific dice positions (0-indexed)
        for pos in positions:
            if 0 <= pos < len(self.dice):
                self.dice[pos] = self.random.randint(1, 6)
        return self.dice
        
    def get_counts(self):
        # Returns dictionary with counts of each value
        return Counter(self.dice)