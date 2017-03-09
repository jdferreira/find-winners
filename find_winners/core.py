#!/usr/bin/env python3

__all__ = [
    'into_hand',
    'find_winners'
]

# The possible suits:
#  C - Clubs
#  D - Diamonds
#  H - Hearts
#  S - Spades
SUITS = 'CDHS'

# The possible values:
#  2-9 - The cards of that face
#  T - 10
#  J - Jack
#  Q - Queen
#  K - King
#  A - Ace
VALUES = '23456789TJQKA'

# The possible ranks in Poker, sorted from highest to lowest
RANKS = [
    'royal_flush',
    'straight_flush',
    'four_of_a_kind',
    'full_house',
    'flush',
    'straight',
    'three_of_a_kind',
    'two_pairs',
    'pair',
    'high_card',
]


class Card:
    """
    Represents a card, which is a pair of value and suit.
    """
    
    def __init__(self, code):
        """
        Initializes a card with the given code. The code is a two-letter string
        where the first letter is the value of the card and the second letter is
        the suit. See the global variables `SUITS` and `VALUES` for the legal
        letters.
        """
        
        self.value = code[0]
        self.suit = code[1]
        
        if self.value not in VALUES:
            raise ValueError('{} is not a valid card value'.format(self.value))
        
        if self.suit not in SUITS:
            raise ValueError('{} is not a valid card suit'.format(self.suit))
    
    
    def __repr__(self):
        return f'{self.value}{self.suit}'
    
    
    def sort_key(self):
        """
        Returns an key that can be used to compare two cards based on their
        value.
        
        Note that this key is only meaningful in a comparison with other
        keys returned from this function.
        """
        
        return VALUES.find(self.value)


def arrange_by_suit(card_set):
    """
    Given a collection of cards, return a dictionary that associates each suit
    with the list of cards of that suit. If the original collection is ordered,
    the order of the cards is kept in the suit lists.
    """
    
    result = {s: [] for s in SUITS}
    for card in card_set:
        result[card.suit].append(card)
    
    return result


def arrange_by_value(card_set):
    """
    Given a collection of cards, return a dictionary that associates each value
    with the list of cards of that value. If the original collection is ordered,
    the order of the cards is kept in the value lists.
    """
    
    result = {v: [] for v in VALUES}
    for card in card_set:
        result[card.value].append(card)
    
    return result


def sort_by_value(card_set):
    """
    Given a collection of cards, return a list of the same cards, ordered by
    value, with the highest card first.
    """
    
    return sorted(card_set, key=Card.sort_key, reverse=True)


def group_by_same_value(by_value):
    """
    Given a collection of cards arranged by value (see `arrange_by_value`),
    cluster the cards into groups of cards of the same value.
    
    The returned value is a list of cards lists, sorted so that the largest
    group is the first item in the list; lists with the same size are sorted
    from highest to lowest value
    """
    
    items = sorted(by_value.items(),
                   key=lambda item: (len(item[1]), item[0]),
                   reverse=True)
    return [lst for _, lst in items if len(lst) != 0]


# def card_value(card):
#     """
#     Returns an integer that can e used to compare two cards based on their
#     value.
#
#     Note that the returned value is only meaningful in a comparison with other
#     values returned from the function.
#     """
#
#     return VALUES.find(card[0])


def all_same_suit(card_set):
    """
    Determines whether the cards in the given collection are all of the same
    suit.
    """
    
    return all(card.suit == card_set[0].suit for card in card_set[1:])


class HandEvaluator:
    
    def __init__(self, hand):
        """
        Initializes a hand evaluator with the given hand.
        
        `hand` is a list of cads
        """
        
        self.hand = hand
        self.cards = None
        
        self.sorted_by_value = sort_by_value(self.hand)
        self.by_suit = arrange_by_suit(self.sorted_by_value)
        self.by_value = arrange_by_value(self.hand)
        self.groups = group_by_same_value(self.by_value)
        
        self.evaluate()
    
    
    def extract_rank(self, rank):
        """
        Runs the function that extracts a given rank from this evaluator's hand.
        """
        
        return getattr(self, 'extract_' + rank)()
    
    
    def evaluate(self):
        """
        This function evaluates a Texas Hold'em hand, which contains seven cards,
        of which 5 will be used to determine the hand's value.
        
        Then returned value is a tuple
            (rank, cards)
        where `rank` is Rank object that can be used to compare two hands, and
        `cards` is the list of 5 cards chosen from the set of seven.
        
        (In fact, the method should work with any set of cards, not just seven, but
        I did not test this.)
        """
        
        for rank in RANKS:
            # The various extract_ functions will set the self.cards variable to
            # the best set of five cards that correspond to the corresponding
            # rank.
            if self.extract_rank(rank):
                return (rank, self.cards)
        
        # The next line will never execute, since one of the `extract_`
        # functions functions will always return a set of five cards (the 'high
        # card' rank will always return a non-None value)
        return None
    
    
    def extract_royal_flush(self):
        """
        Extracts five cards from the hand corresponding to a "Royal Flush".
        
        A "Royal Flush" is a set of five consecutive cards of the same suit,
        from Ace to Ten.
        """
        
        if self.extract_straight_flush() and self.cards[-1].value == 'T':
            return True
        else:
            # If we did not pass the conditions, set the cards back to `None`
            self.cards = None
            return False
    
    
    def extract_straight_flush(self):
        """
        Extracts five cards from the hand corresponding to a "Straight Flush".
        
        A "Straight Flush" is a set of five consecutive cards of the same suit.
        """
        
        if self.extract_straight() and all_same_suit(self.cards):
            return True
        else:
            # If we did not pass the conditions, set the cards back to `None`
            self.cards = None
            return False
    
    
    def extract_four_of_a_kind(self):
        """
        Extracts five cards from the hand corresponding to "Four of a Kind".
        
        A "Four of a Kind" is a set of four cards of the same value. If two
        players share the same Four of a Kind, the bigger fifth card
        (the "kicker") decides who wins the pot.
        """
        
        return self.extract_n_of_a_kind(4)
    
    
    def extract_full_house(self):
        """
        Extracts five cards from the hand corresponding to a "Full House".
        
        A "Full House" is any three cards of the same value together with any
        two cards of the same value. The set of three cards defines who wins.
        """
        
        # We need to have three of a kind and at least 2 of a kind for the next
        # value to make a full house
        if len(self.groups[0]) == 3 and len(self.groups[1]) >= 2:
            self.cards = self.groups[0] + self.groups[1][:2]
            return True
        else:
            return False
        
    
    
    def extract_flush(self):
        """
        Extracts five cards from the hand corresponding to a "Flush".
        
        A "Flush" is a set of five cards all of the same suit
        """
        
        flush = [lst for lst in self.by_suit.values() if len(lst) == 5]
        if not flush:
            return False
        
        # Grab the highest-value flush (which is only important if the size of
        # the hand is 10 or more)
        flush.sort(key=lambda x: x[0].sort_key(), reverse=True)
        self.cards = list(flush)[0]
        
        return True
    
    
    def extract_straight(self):
        """
        Extracts five cards from the hand corresponding to a "Straight".
        
        A "Straight" is a set of five consecutive cards, irrespecitve of suit.
        """
        
        # slots = {
        #     value: [card for card in self.hand if card.value == value]
        #     for value in VALUES
        # }
        
        sequential = 'AQKJT98765432A'
        sequences = [sequential[i:i+5] for i in range(len(sequential) - 4)]
        for sequence in sequences:
            if all(len(self.by_value[v]) > 0 for v in sequence):
                # We found a straight
                self.cards = [self.by_value[v][0] for v in sequence]
                # WRONGS!!!!!!!!! Needs to select from the same suit!
                return True
        
        return False
    
    
    def extract_three_of_a_kind(self):
        """
        Extracts five cards from the hand corresponding to a "Three of a Kind".
        
        A "Three of a Kind" is a set of three cards of the same value. If two
        players share the same Three of a Kind, the bigger fourth and fifth
        cards decide who wins the pot.
        """
        
        return self.extract_n_of_a_kind(3)
    
    
    def extract_two_pairs(self):
        """
        Extracts five cards from the hand corresponding to a
        """
        
        # We need to have two pairs
        if len(self.groups[0]) == 2 and len(self.groups[1]) == 2:
            self.cards = self.groups[0] + self.groups[1]
            self.complete_hand()
            return True
        else:
            return False
    
    
    def extract_pair(self):
        """
        Extracts five cards from the hand corresponding to a "Pair".
        
        A "Pair" is a set of two cards of the same value. If two players share
        the same Pair, the bigger third, fourth and fifth cards decide who wins
        the pot.
        """
        
        return self.extract_n_of_a_kind(2)
    
    
    def extract_high_card(self):
        """
        Extracts five cards from the hand corresponding to a
        """
        
        self.cards = self.sorted_by_value[:5]
        return True
    
    
    def extract_n_of_a_kind(self, n):
        """
        Extracts five cards from the hand corresponding to a "Four of a Kind",
        "Three of a Kind" or a "Pair". The code is the same for any of these
        ranks, only changing the `n`, which is 4, 3 and 2 respectively.
        """
        
        # Only return True if the maximum set of cards of the same value has
        # size `n`; otherwise, exit early
        if self.groups[0][0] != n:
            return False
        
        self.cards = self.groups[0][1]
        self.complete_hand()
        
        return True
    
    
    def complete_hand(self):
        # We need to add the highest remaining cards to the final set
        # to allow it to be compared to the other player sets.
        for card in self.sorted_by_value:
            if card not in self.cards:
                self.cards.append(card)
                if len(self.cards) == 5:
                    # We have reached the end of the final hand of 5 cards.
                    break
        
        # Notice that enough cards will have been added at this moment, since
        # the initial hand contains 5 or more cards. This means that the `break`
        # in the previous for-loop is guaranteed to be executed.


def hand_key(hand):
    """
    Returns an key that can be used to compare two hands.
    
    Note that this key is only meaningful in a comparison with other
    keys returned from this function.
    """
    
    h = HandEvaluator(hand)
    rank, cards = h.evaluate()
    
    rank = len(RANKS) - RANKS.index(rank)
    card_keys = [Card.sort_key(c) for c in cards]
    
    return rank, card_keys


def into_hand(hand):
    return [Card(code) for code in hand.split()]


def find_winners(hands):
    hands_ranks = [(hand_key(hand), idx) for idx, hand in enumerate(hands)]
    hands_ranks.sort(reverse=True)

    max_rank = hands_ranks[0]
    winners = [hands_ranks[0][1]]
    for key, idx in hands_ranks[1:]:
        if key == max_rank:
            winners.append(idx)
        else:
            break

    return winners
