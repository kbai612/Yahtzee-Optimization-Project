import random
from collections import Counter
from scoreboard import YahtzeeScorer # Assuming YahtzeeScorer is accessible

def yahtzee_focus_strategy(dice, scorecard, simulator):
    """
    A Yahtzee strategy that aggressively tries to roll a Yahtzee.
    """
    available_categories = [cat for cat, score in scorecard.items() if score is None]
    straight_categories = ['small_straight', 'large_straight']
    available_straight = [cat for cat in available_categories if cat in straight_categories]
    straight_potential = [2 and 3, 3 and 4, 4 and 5]
    upper_categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    available_upper = [cat for cat in available_categories if cat in upper_categories]
    available_lower = [cat for cat in available_categories if cat not in upper_categories and cat != 'yahtzee'] # Exclude yahtzee if not scored

    
    for roll_num in range(2):
        # --- Rerolling Logic ---
        counts = Counter(dice)
        
        # Find the number that appears most often (must be at least 2 times)
        most_common_val = -1
        max_count = 1 
        for num, count in counts.items():
            if count > max_count:
                max_count = count
                most_common_val = num
            elif count == max_count and num > most_common_val: # Prefer higher number in case of tie
                most_common_val = num
            
        dice_to_keep = []
        if max_count >= 2: # If we have at least a pair, keep those dice
            dice_to_keep = [i for i in dice if dice == most_common_val]
        elif 'yahtzee' in available_categories: # If no pair, but Yahtzee category available, reroll all
            dice_to_keep = []
        else:  # If no pair and Yahtzee category unavailable look for straight
            unique_sorted_dice = sorted(list(set(dice)))
            longest_sequence, current_sequence = [], []
            for i in range(len(unique_sorted_dice)):
                if not current_sequence or unique_sorted_dice[i] == current_sequence[-1] + 1:
                    current_sequence.append(unique_sorted_dice[i])
                else:
                    if len(current_sequence) > len(longest_sequence): longest_sequence = current_sequence
                    current_sequence = [unique_sorted_dice[i]]
            if len(current_sequence) > len(longest_sequence): longest_sequence = current_sequence
            
            target_dice_values = []
            # Keep sequence if length > 1
            if len(longest_sequence) > 1:
                target_dice_values = longest_sequence
            # Otherwise, keep the highest die
            else:
                target_dice_values = [max(dice)]
            
            # Collect all dice from the original hand matching the target values
            temp_dice_to_keep = [d for d in dice if d in target_dice_values]

        # Determine positions to reroll based on the dice we decided to keep
        indices_to_keep = []
        temp_hand = list(simulator.hand.dice) 
        temp_dice_to_keep = list(dice_to_keep)

        # Find indices of dice to keep, handling duplicates correctly
        for i in range(len(temp_hand)):
            die = temp_hand[i]
            if die in temp_dice_to_keep:
                indices_to_keep.append(i)
                temp_dice_to_keep.remove(die) # Remove one instance to match duplicates
        
        # --- Perform Reroll ---
        # Determine indices to reroll
        reroll_positions = [i for i in range(len(simulator.hand.dice)) if i not in indices_to_keep]

        if reroll_positions:
             simulator.hand.reroll(reroll_positions)
             dice = list(simulator.hand.dice)
        else:
            break # No reroll needed if all dice are kept

    final_counts = Counter(dice)

    # --- Scoring Logic ---
    best_score = -1
    best_category = None
    is_yahtzee = 5 in final_counts.values()

    # Prioritize scoring Yahtzee if available and achieved
    if 'yahtzee' in available_categories and is_yahtzee:
        best_category = 'yahtzee'
        best_score = simulator.scorer.score_yahtzee(dice) # Should be 50
    
    # If Yahtzee category used OR not achieved, find the best score elsewhere
    else:
        for category in available_categories:
            score_method = getattr(simulator.scorer, f"score_{category}")
            score = score_method(dice)
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