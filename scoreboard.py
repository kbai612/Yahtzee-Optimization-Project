from collections import Counter

class YahtzeeScorer:
    # Upper Section Scores
    @staticmethod
    def score_ones(dice):
        return sum(d for d in dice if d == 1)
    @staticmethod
    def score_twos(dice):
        return sum(d for d in dice if d == 2)
    @staticmethod
    def score_threes(dice):
        return sum(d for d in dice if d == 3)
    @staticmethod
    def score_fours(dice):
        return sum(d for d in dice if d == 4)
    @staticmethod
    def score_fives(dice):
        return sum(d for d in dice if d == 5)
    @staticmethod
    def score_sixes(dice):
        return sum(d for d in dice if d == 6)

    # Lower Section Scores
    @staticmethod
    def score_three_of_a_kind(dice):
        counts = Counter(dice)
        if any(count >= 3 for count in counts.values()):
            return sum(dice)
        return 0
    @staticmethod
    def score_four_of_a_kind(dice):
        counts = Counter(dice)
        if any(count >= 4 for count in counts.values()):
            return sum(dice)
        return 0
    @staticmethod
    def score_full_house(dice):
        counts = list(Counter(dice).values())
        if sorted(counts) == [2, 3]:
            return 25
        return 0
    @staticmethod
    def score_small_straight(dice):
        unique_sorted = sorted(set(dice))
        if len(unique_sorted) >= 4 and max(unique_sorted) - min(unique_sorted) == len(unique_sorted) - 1:
            return 30
        return 0
    @staticmethod
    def score_large_straight(dice):
        unique_sorted = sorted(set(dice))
        if len(unique_sorted) == 5 and max(unique_sorted) - min(unique_sorted) == 4:
            return 40
        return 0
    @staticmethod
    def score_yahtzee(dice):
        if len(set(dice)) == 1:
            return 50
        return 0
    @staticmethod
    def score_chance(dice):
        return sum(dice)
