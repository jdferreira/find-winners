from core import *

with open('find-winners-input.txt') as f:
    hands = [into_hand(line.rstrip('\n')) for line in f]

print('\n'.join(str(i) for i in find_winners(hands)))
