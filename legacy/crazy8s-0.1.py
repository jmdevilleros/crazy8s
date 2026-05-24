# ----------------------------------------------------------------------
# crazy8s-0.1.py
# Crazy Eights
# ----------------------------------------------------------------------


from cards import Card, FrenchDeck # uses v0.2
import random 
import os
import time


# Open deck and shuffle it
deck = FrenchDeck.create()
random.shuffle(deck)

# Deal cards to player
hand1 = [deck.pop() for card in range(7)]

# Put top card of deck on discard
discard = [deck.pop()]

# Turn cards in deck
for card in deck:
    card.facedown = True

dump = input("Enter para iniciar")

iteration = 0
valid_suit = discard[-1].suit
while True:
    dump = os.system("clear")
    
    iteration += 1
    print("Iteration:", iteration)
    
    print("\nHand1:   ", len(hand1), hand1)
    print("\nDiscard: ", len(discard), discard)
    print("\nDeck:    ", len(deck), deck)

    if len(hand1) < 1:
        print("\n\n*** WIN ***")
        break

    valid_rank = discard[-1].rank 

    # Find possible cards to play 
    candidates = [
        card for card in hand1 
            if card.suit == valid_suit \
               or card.rank == valid_rank \
               or card.rank == "8"
    ]
    print("\nCandidates in hand1: ", candidates)

    # If there are candidate cards, select one
    if len(candidates) > 0:
        elected = candidates[-1] # Basic choice: last card
        print("\nPlaying:", elected)

        # Play the card on top of discard pile
        discard.append(hand1.pop(hand1.index(elected)))
        
        # If a crazy 8 was selected, choose next suit
        if elected.rank == "8" and len(hand1) > 0:
            valid_suit = hand1[-1].suit
        else:
            valid_suit = discard[-1].suit
            
        print("Next suit: ", valid_suit)

    else: 
        # No card to play, draw one from deck and show it in hand
        # If deck is empty, leave top card in discard pile and
        # reshuffle the rest as new drawing deck
        if len(deck) < 1:
            # If discard is empty, every card is in hand. Game closed
            if len(discard) < 1:
                print("\nGame Over")
                break
                
            deck = discard
            discard = [deck.pop()]
            for card in deck:
                card.facedown = True
            shuffle(deck)
            print("\nReshuffling.")
            print("  New discard: ", discard)
            print("  New deck   : ", deck)
            #time.sleep(5)
       
        draw = deck.pop()
        draw.facedown = False
        print("\nDrawing: ", draw)
        hand1.append(draw)

    # time.sleep(1)
    # Turn ends
    if input("\nq to exit loop ") == "q":
       break

input("\nPress ENTER...")
