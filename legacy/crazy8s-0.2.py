# ----------------------------------------------------------------------
# crazy8s-0.2.py
# Crazy Eights
# ----------------------------------------------------------------------


from cards import FrenchDeck # uses v0.3
import os

# ----------------------------------------------------------------------

class Crazy8s():
    """ Container class for crazy 8s game """

    def __init__(self, players=1):
        self.deck = FrenchDeck.create()
        self.deck.shuffle()
        self.setplayers(players)
        self.discard = self.deck.deal(1)
        self.deck.facedown()
        self.iteration = 0
        self.winner = None
        self.next_suit = self.discard.cards[-1].suit
        self.next_rank = self.discard.cards[-1].rank
        
    def setplayers(self, numplayers):
        hand_size = 7 if numplayers < 3 else 5
        self.players = [
            self.deck.deal(hand_size) for player in range(numplayers)
        ]
                    
    def play(self):
        game = self
        while True:
            game.iteration += 1
            if game.has_winner():
                break
            for player,hand in enumerate(game.players):
                game.display(game.iteration, player)
                game.playerturn(player,hand)
        return self.winner

    def has_winner(self):
        for player,hand in enumerate(self.players):
            if len(hand.cards) < 1:
                self.winner = player
                return True
        return False

    def playerturn(self, player, hand):
        # Find possible cards to play 
        candidates = [
            card for card in hand.cards 
                if card.rank == "8" \
                   or card.suit == self.next_suit \
                   or card.rank == self.next_rank
        ]
        # If there are candidate cards, select one
        if len(candidates) > 0:
            elected = candidates[-1] # Basic choice: last card

            # Play the card on top of discard pile
            discard = self.discard.cards
            discard.append(hand.cards.pop(hand.cards.index(elected)))
            
            self.next_rank = discard[-1].rank 
              
            # If a crazy 8 was selected, choose next suit
            if elected.rank == "8" and len(hand.cards) > 0:
                self.next_suit = hand.cards[-1].suit
            else:
                self.next_suit = discard[-1].suit
        else:
            # No playable card, must draw
            hand.cards.append(self.drawcard())

    def drawcard(self):
        # If deck is empty, leave top card in discard pile and
        # reshuffle the rest as new drawing deck
        if len(self.deck.cards) < 1:
            self.deck = self.discard
            self.discard = self.deck.deal(1,facedown=False)
            self.deck.flip()
            self.deck.shuffle()
       
        return self.deck.draw(facedown=False)

    def display(self, iteration, player):
        os.system("clear")
        print("Iteration: ", iteration)
        print("Player: ", player+1)
        for n,hand in enumerate(self.players):
            print("\nPlayer ", n+1, hand)
        print("\nDiscard: ", self.discard)
        print("\nDeck: ", self.deck)
        print("\nNext suit: ", self.next_suit)
        print("Next rank: ", self.next_rank)
        input("\nEnter to continue...")
        
# ----------------------------------------------------------------------

game = Crazy8s(players=2)
result = game.play()

print("\n-------------------\nResult: Winner is player", result+1)
input("\nPress ENTER to exit")
