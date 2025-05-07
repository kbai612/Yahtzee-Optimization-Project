import random
from collections import Counter
from scoreboard import YahtzeeScorer # Assuming YahtzeeScorer is accessible
from dice_rolling import YahtzeeHand # May need hand methods

def get_straight_length(dice):
    """Helper to find the length of the longest straight in a set of dice."""
    unique_sorted = sorted(list(set(dice)))
    max_len = 0
    current_len = 0
    if not unique_sorted:
        return 0
    
    max_len = 1
    current_len = 1
    for i in range(len(unique_sorted) - 1):
        if unique_sorted[i+1] == unique_sorted[i] + 1:
            current_len += 1
        else:
            current_len = 1 # Reset sequence
        max_len = max(max_len, current_len)
    return max_len

def find_best_initial_target(dice, available_categories):
    """Analyzes the initial dice roll to pick a target category."""
    counts = Counter(dice)
    sorted_dice = sorted(dice)
    straight_len = get_straight_length(dice)
    
    # Priority: Check for best potential based on initial roll
    
    # 1. Yahtzee?
    if 5 in counts.values() and 'yahtzee' in available_categories:
        return 'yahtzee'
        
    # 2. Large Straight?
    if straight_len >= 5 and 'large_straight' in available_categories:
        return 'large_straight'
        
    # 3. Four of a Kind?
    if 4 in counts.values() and 'four_of_a_kind' in available_categories:
        return 'four_of_a_kind'
        
    # 4. Full House?
    has_triple = False
    has_pair = False
    triple_val = -1
    for num, count in counts.items():
        if count == 3:
            has_triple = True
            triple_val = num
        if count == 2:
            has_pair = True
    if has_triple and has_pair and 'full_house' in available_categories:
        return 'full_house'

    # 5. Small Straight?
    if straight_len >= 4 and 'small_straight' in available_categories:
        return 'small_straight'

    # 6. Three of a Kind?
    if 3 in counts.values() and 'three_of_a_kind' in available_categories:
        # Also consider if this triple could lead to a better FH or 4oak
        if 'full_house' in available_categories or 'four_of_a_kind' in available_categories:
             # Maybe prioritize keeping the triple for those? Let's stick to 3oak for now if it's the best direct match.
             pass 
        return 'three_of_a_kind'

    # 7. Upper Section - Prioritize higher numbers or most numerous
    upper_categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    available_upper = [cat for cat in available_categories if cat in upper_categories]
    if available_upper:
        best_upper_target = None
        best_upper_count = 0
        # Find the available upper category with the most dice already present
        for i in range(6, 0, -1): # Check 6s down to 1s
            cat_name = upper_categories[i-1]
            if cat_name in available_upper:
                current_count = counts.get(i, 0)
                if current_count > best_upper_count:
                    best_upper_count = current_count
                    best_upper_target = cat_name
        if best_upper_target and best_upper_count > 0: # Found a reasonable upper target
             return best_upper_target

    # 8. Fallback: Chance or just pick one if nothing else fits
    if 'chance' in available_categories:
        return 'chance'
    elif available_categories:
        # Default to an available upper category if possible, otherwise random
        if available_upper: return available_upper[0] 
        else: return random.choice(available_categories)
    else:
        return 'chance' # Should not happen

def tunnel_vision_strategy(dice, scorecard, simulator):
    """
    A Yahtzee strategy that picks a target based on the initial roll,
    then rerolls specifically for that target.
    """
    available_categories = [cat for cat, score in scorecard.items() if score is None]
    straight_categories = ['small_straight', 'large_straight']
    available_straight = [cat for cat in available_categories if cat in straight_categories]
    straight_potential = [2 and 3, 3 and 4, 4 and 5]
    upper_categories = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    available_upper = [cat for cat in available_categories if cat in upper_categories]
    available_lower = [cat for cat in available_categories if cat not in upper_categories and cat != 'yahtzee'] # Exclude yahtzee if not scored
    
    # --- Determine Target Category based on Initial Roll ---
    initial_dice = list(dice) # The dice state *before* any rerolls in this turn
    target_category = find_best_initial_target(initial_dice, available_categories)

    # --- Rerolling Logic - Focused on the Target Category ---
    for roll_num in range(2): # Perform up to two rerolls
        counts = Counter(initial_dice)
        keep_indices = []

        # Determine dice to keep based *only* on the target_category
        if target_category in ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']:
            target_num = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes'].index(target_category) + 1
            keep_indices = [i for i, die in enumerate(initial_dice) if die == target_num]
        
        elif target_category == 'three_of_a_kind' or target_category == 'four_of_a_kind' or target_category == 'yahtzee':
            # Keep the dice that form the largest group
            most_common_num = -1
            max_count = 0
            for num, count in counts.items():
                 if count > max_count:
                     max_count = count
                     most_common_num = num
                 elif count == max_count and num > most_common_num: # Tie-break high
                     most_common_num = num
            if max_count > 0: # Should always be true unless hand is empty
                 keep_indices = [i for i, die in enumerate(initial_dice) if die == most_common_num]

        elif target_category == 'full_house':
            # Keep all dice part of the best triple and best pair found
            triple_val = -1
            pair_val = -1
            found_triple = False
            found_pair = False
            sorted_counts = counts.most_common() # List of (value, count) sorted by count desc

            if sorted_counts and sorted_counts[0][1] >= 3:
                 triple_val = sorted_counts[0][0]
                 found_triple = True
                 # Look for a pair among the rest
                 for val, count in sorted_counts[1:]:
                     if count >= 2:
                         pair_val = val
                         found_pair = True
                         break
            elif sorted_counts and sorted_counts[0][1] >= 2: # Didn't find triple, look for best pair
                 pair_val = sorted_counts[0][0]
                 found_pair = True
                 # Look for another pair (or triple treated as pair)
                 if len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
                      # This could be the triple if the first was only a pair
                      if triple_val == -1: triple_val = sorted_counts[1][0] # Treat second pair as the 'triple' base
                      found_triple = True # Mark as found for keeping logic

            # Keep dice matching the identified triple/pair values
            if found_triple:
                 keep_indices.extend([i for i, die in enumerate(initial_dice) if die == triple_val])
            if found_pair:
                 # Avoid adding same indices twice if pair_val is same as triple_val (e.g., Yahtzee)
                 keep_indices.extend([i for i, die in enumerate(initial_dice) if die == pair_val and i not in keep_indices])
            # Remove duplicates just in case
            keep_indices = list(set(keep_indices))


        elif target_category == 'small_straight' or target_category == 'large_straight':
            # Keep the dice forming the longest straight sequence found
            unique_sorted = sorted(list(set(initial_dice)))
            best_seq = []
            current_seq = []
            if unique_sorted:
                current_seq = [unique_sorted[0]]
                for i in range(len(unique_sorted) - 1):
                    if unique_sorted[i+1] == unique_sorted[i] + 1:
                        current_seq.append(unique_sorted[i+1])
                    else:
                        if len(current_seq) > len(best_seq):
                            best_seq = current_seq
                        current_seq = [unique_sorted[i+1]] # Start new sequence
                if len(current_seq) > len(best_seq): # Check last sequence
                    best_seq = current_seq

            # Keep one of each die value in the best sequence found
            if best_seq:
                 temp_indices = []
                 needed = list(best_seq)
                 for idx, die in enumerate(initial_dice):
                     if die in needed:
                         temp_indices.append(idx)
                         needed.remove(die) # Remove one instance
                 keep_indices = temp_indices

        elif target_category == 'chance':
            # Keep high dice (e.g., 4, 5, 6)
            keep_indices = [i for i, die in enumerate(initial_dice) if die >= 4]


        # --- Perform Reroll ---
        dice_to_reroll_count = 5 - len(keep_indices)
        
        if dice_to_reroll_count == 0: # Already keeping all dice
             break 
        
        indices_to_reroll = [i for i in range(5) if i not in keep_indices]

        if dice_to_reroll_count > 0:
             simulator.hand.reroll(indices_to_reroll)
             initial_dice = list(simulator.hand.dice) # Update initial_dice

    final_dice = tuple(initial_dice)

    # --- Category Selection Logic ---
    # Score the category we originally targeted for this turn.
    # Check if it's still available (it should be unless game logic is flawed)
    if target_category in available_categories:
        return target_category, final_dice
    else:
        # Fallback: If target somehow became unavailable, pick best available score
        best_fallback_score = -1
        best_fallback_category = None
        for category in available_categories:
            score_method = getattr(simulator.scorer, f"score_{category}")
            score = score_method(dice)
            if score > best_score:
                best_score = score
                best_category = category
        
        if best_fallback_category:
             return best_fallback_category, final_dice
        elif available_categories: # If all scores are 0, pick one to zero out
             return available_categories[0], final_dice
        else: # No categories left
             return 'chance', final_dice # Should not happen