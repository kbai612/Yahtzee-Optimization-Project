import random
from collections import Counter
from scoreboard import YahtzeeScorer

def upper_focus_strategy(dice, scorecard, simulator):
    """
    A Yahtzee strategy that prioritizes scoring in the upper section categories
    to achieve the bonus.
    """
    available_categories = [cat for cat, score in scorecard.items() if score is None]
    upper_categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    available_upper = [cat for cat in available_categories if cat in upper_categories]
    available_lower = [cat for cat in available_categories if cat not in upper_categories and cat != 'yahtzee'] # Exclude yahtzee if not scored

    
    # --- Rerolling Logic ---
    for roll_num in range(2): # Perform up to two rerolls
        counts = Counter(dice)
        keep_indices = []

        # Determine best upper category target currently available
        best_target_num = 0
        if available_upper:
            # Prioritize higher numbers first if available
            for num in range(6, 0, -1):
                 num_str = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes'][num-1]
                 if num_str in available_upper:
                     best_target_num = num
                     break

        # Keep dice matching the best target number
        if best_target_num > 0:
            for i, die in enumerate(dice):
                if die == best_target_num:
                    keep_indices.append(i)


        # --- Perform Reroll ---
        dice_to_reroll_count = 5 - len(keep_indices)
        
        # No dice to reroll (all kept)
        if dice_to_reroll_count == 0: 
             break
        
        # Determine indices to reroll
        indices_to_reroll = [i for i in range(5) if i not in keep_indices]

        if dice_to_reroll_count > 0:
             # Use the correct reroll method from YahtzeeHand
             simulator.hand.reroll(indices_to_reroll)
             dice = list(simulator.hand.dice) 

    # --- Scoring Logic ---
    best_score = -1
    best_category = None

    # Prioritize available upper categories
    if available_upper:
        for category in available_upper:
            score_method = getattr(simulator.scorer, f"score_{category}")
            score = score_method(dice)
            target_num = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes'].index(category) + 1
            # If we have at least one of the dice in the category and score is better than current best
            if counts.get(target_num, 0) > 0 and score > best_score: 
                 best_score = score
                 best_category = category

    # If no suitable upper category found or scored, consider all available categories
    if best_category is None:
        best_score = -1 
        for category in available_categories:
            score_method = getattr(simulator.scorer, f"score_{category}")
            score = score_method(dice)
            # If score is better than current best then update
            if score > best_score:
                best_score = score
                best_category = category

    # If no category yields a score > 0 (or all taken), pick a category to zero out
    if best_category is None:
         # Try to zero out a less valuable category first.
         if available_upper:
             # Zero out the lowest available upper category first
             best_category = min(available_upper, key=lambda cat: simulator.upper_categories.index(cat))
         elif available_lower:
              # Zero out 'chance' or 'three_of_a_kind' if available
              if 'chance' in available_lower: best_category = 'chance'
              elif 'three_of_a_kind' in available_lower: best_category = 'three_of_a_kind'
              else: best_category = random.choice(available_lower) # Random lower if others taken
         elif 'yahtzee' in available_categories: # Only remaining option is Yahtzee, score 0
              best_category = 'yahtzee'
         else:
              # Should not happen in a normal game
              return 'chance', dice # Absolute fallback

    return best_category, dice