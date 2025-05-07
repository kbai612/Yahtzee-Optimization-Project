from collections import Counter
import random

def straight_strategy(dice, scorecard, simulator):
    """
    A Yahtzee strategy that prios looking for straights
    then rerolls to try to get the largest straight.
    """
    available_categories = [cat for cat, score in scorecard.items() if score is None]
    straight_categories = ['small_straight', 'large_straight']
    available_straight = [cat for cat in available_categories if cat in straight_categories]
    straight_potential = [2 and 3, 3 and 4, 4 and 5]
    upper_categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    available_upper = [cat for cat in available_categories if cat in upper_categories]
    available_lower = [cat for cat in available_categories if cat not in upper_categories and cat != 'yahtzee'] # Exclude yahtzee if not scored

    # Make up to two more rolls
    for _ in range(2):
        # --- Rerolling Logic ---
        counts = Counter(dice)
        max_count = 0

        common_list = counts.most_common(1)
        if common_list:
                max_count = common_list[0][1]

        dice_to_keep = []
        if available_straight and any(i in available_categories for i in straight_potential):
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
        elif max_count > 1:
            most_common_val = counts.most_common(1)[0][0]
            dice_to_keep = [d for d in dice if d == most_common_val]
        else:
            dice_to_keep = []

        # Determine positions to reroll based on the dice we decided to keep
        indices_to_keep = []
        temp_hand = list(simulator.hand.dice) # Get current hand state
        temp_dice_to_keep = list(dice_to_keep) # Copy list to allow removal

        # Find indices of dice to keep, handling duplicates correctly
        for i in range(len(temp_hand)):
            die = temp_hand[i]
            if die in temp_dice_to_keep:
                indices_to_keep.append(i)
                temp_dice_to_keep.remove(die) # Remove one instance to match duplicates

        # --- Perform Reroll ---
        reroll_positions = [i for i in range(len(simulator.hand.dice)) if i not in indices_to_keep]
        # Perform reroll only if there are dice to reroll
        if reroll_positions:
            simulator.hand.reroll(reroll_positions)
            dice = simulator.hand.dice # Update dice state
        else:
            # If keeping all dice, no need for further rerolls in this turn
            break
            
    # Score in the category that gives the highest points
    available_categories = [cat for cat in scorecard if scorecard[cat] is None]
    best_score = -1
    best_category = None
    
    # Ensure dice is always a list for scoring methods
    if not isinstance(dice, list):
        # This case shouldn't happen if simulator.hand.dice is always a list, but good practice
        dice = list(dice)

    for category in available_categories:
            score_method = getattr(simulator.scorer, f"score_{category}")
            score = score_method(dice)
            if score > best_score:
                best_score = score
                best_category = category

    # If no suitable category was found (e.g., all filled or errors), choose the first available one to score 0
    if best_category is None and available_categories:
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
    
    # Return the chosen category and the final state of the dice
    return best_category, dice
