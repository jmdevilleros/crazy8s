# ----------------------------------------------------------------------
# Crazy 8 stats
# ----------------------------------------------------------------------


from crazy8s import Crazy8s # Uses v0.9
from players import Player
from cards import FrenchDeck, CardStack
import sys
import random


RANGE = 20000 if len(sys.argv)<2 else int(sys.argv[1])
PLAYERS = 9 if len(sys.argv)<3 else int(sys.argv[2])

# ----------------------------------------------------------------------
def sel_random(game, candidates):
    if candidates:
        hand = game.current_player.data[0]
        card = random.choice(candidates)  
        if card.rank == game.CRAZY8:
            suit = random.choice(list(hand.suits()))
        else:
            suit = card.suit
    else:
        card, suit = None, None
    return card, suit

# ----------------------------------------------------------------------
def sel_ranking1(game, candidates):
    if candidates:
        hand = game.current_player.data[0]
        discard = game.discard
        card = max((card for card in candidates), 
                    key=lambda c: ranking1(c, hand, discard))
        if card.rank == game.CRAZY8:
            suit = nextcrazysuit(hand)
        else:
            suit = card.suit
    else:
        card, suit = None, None
    return card, suit

# ----------------------------------------------------------------------
def sel_ranking2(game, candidates):
    if candidates:
        hand = game.current_player.data[0]
        discard = game.discard
        card = max((card for card in candidates), 
                    key=lambda c: ranking2(c, hand, discard))
        if card.rank == game.CRAZY8:
            suit = nextcrazysuit(hand)
        else:
            suit = card.suit
    else:
        card, suit = None, None
    return card, suit

# ----------------------------------------------------------------------
def sel_user(game, candidates):
    hand = game.current_player.data[0]
    game.displaystate(display=True, pause=True)
    hand.flip()
    game.displaystate(display=True, pause=True)
    if candidates:
        card = choose(candidates)
        if card.rank == game.CRAZY8:
            suit = choose(FrenchDeck.SUITS)
        else:
            suit = card.suit
    else:
        card, suit = None, None
    hand.flip()
    return card, suit

# ----------------------------------------------------------------------
def ranking1(card, hand, discard):
    initial = -52*7 if card.rank == "8" else 0 
    same_suit_in_hand = len(list(hand.search(suits=[card.suit])))
    same_rank_in_hand = len(list(hand.search(ranks=[card.rank])))
    same_suit_in_discard = len(list(discard.search(suits=[card.suit])))
    same_rank_in_discard = len(list(discard.search(ranks=[card.rank])))
    return initial + same_suit_in_hand \
                   + same_rank_in_hand  \
                   + same_suit_in_discard \
                   + same_rank_in_discard 
# ----------------------------------------------------------------------
def ranking2(card, hand, discard):
    initial = -52*7 if card.rank == "8" else 0 
    same_suit_in_hand = len(list(hand.search(suits=[card.suit])))
    same_rank_in_hand = len(list(hand.search(ranks=[card.rank])))
    same_suit_in_discard = len(list(discard.search(suits=[card.suit])))
    same_rank_in_discard = len(list(discard.search(ranks=[card.rank])))
    return initial + same_suit_in_hand  \
                   + same_rank_in_hand * 4 \
                   + same_suit_in_discard   \
                   + same_rank_in_discard * 4

# ----------------------------------------------------------------------
def nextcrazysuit(hand):
    no8 = CardStack(hand.search(ranks=["8"], negate=True))
    if len(no8) > 0:
        crazysuit = max((suit for suit in set(no8.suits())),
                        key=lambda s: len(list(no8.search(suits=[s]))))
    else:
        crazysuit = None
    return crazysuit

# ----------------------------------------------------------------------
def choose(iterable, title="Choices", prompt="Choice?"):
    options = list(iterable)
    selected = None
    while (selected == None) and options:
        print("\n{}".format(title))
        for num, option in enumerate(options):
            print(num, option)
        try:
            selected = options[int(input(prompt))]
        except (ValueError, IndexError):
            pass
        except:
            raise
    return selected
    
# ----------------------------------------------------------------------
sumturns = 0
minturns = 9999
maxturns = 0
sumreshuffles = 0
sumemptydraws = 0
sumwins = {}

players = Player.createlist(PLAYERS)

for seq in range(RANGE):
    title = "Crazy8 test game #" + str(seq + 1)
    game = Crazy8s(players=players, title=title)

    game.initialize()

    for i, f in enumerate([sel_ranking1, sel_ranking2, sel_random]):
        players[i].data[1] = f
        players[i].name = f.__name__

    game.play(display=False, delay=0, pause=False)
    winner = game.winner
    sumturns += game.current_turn
    sumreshuffles += game.reshuffles
    sumemptydraws += game.emptydraws
    minturns = game.current_turn if game.current_turn < minturns else minturns
    maxturns = game.current_turn if game.current_turn > maxturns else maxturns
    if winner.name in sumwins:
        sumwins[winner.name] += 1
    else:  
        sumwins[winner.name] = 1

    print("Game={:07d} "
            "Turns={:<3} "
            "Reshuffles={:<2} "
            "Empty_draws={:<2} "
            "winner={:12}".format(
            seq + 1, 
            game.current_turn, 
            game.reshuffles,
            game.emptydraws,
            winner.name))
    
    del game

print("\nTurns: Avg={}, Min={}, Max={}:".format(
      sumturns/RANGE, minturns, maxturns))
print("Reshuffles: Avg={}".format(sumreshuffles/RANGE))
print("Empty draws: Avg={}\n".format(sumemptydraws/RANGE))
      
for player,totalwins in sorted(sumwins.items()):
    if totalwins > 0:
        print("{} wins {} times ({:0.2f}%)".format(
                player, totalwins, totalwins/RANGE*100))


#while True:
#    if input("\nq to exit ") == "q":
#        break

