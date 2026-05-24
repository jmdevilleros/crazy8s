# ----------------------------------------------------------------------
# crazy8s-0.3.py
# Crazy Eights
# ----------------------------------------------------------------------


from cards import FrenchDeck # uses v0.4
import os
import time


# ----------------------------------------------------------------------

class Crazy8s():
    """ Container class for crazy 8s game """

    CRAZY8 = "8"
    
    # ------------------------------------------------------------------
    class Player():
        """ Player data: Name and cards in hand """
        def __init__(self, name, hand):
            self.name = name
            self.hand = hand

    # ------------------------------------------------------------------
    def __init__(self, title="Crazy8", players=1):
        self.title = title
        self.deck = FrenchDeck.create()
        self.deck.shuffle()
        self.players = self.setplayers(players)
        self.discard = self.deck.deal(1)
        self.deck.facedown()
        self.next_suit = self.discard.top().suit
        self.next_rank = self.discard.top().rank
        self.winner = None
        self.turn = 0
    
    # ------------------------------------------------------------------    
    def setplayers(self, numplayers):
        hand_size = 7 if numplayers < 3 else 5
        players = []
        for player in range(numplayers):
            name = "Player" + str(player + 1)
            hand = self.deck.deal(hand_size, facedown=True)
            players.append(self.Player(name, hand))
        return players
               
    # ------------------------------------------------------------------                
    def play(self, display=True, delay=0, pause=True):
        """ Game loop """
        
        self.displaystate(display, delay, pause)
        while True:
            self.turn += 1
            for player in self.players:
                player.hand.flip()
                self.displaystate(display, delay, pause)

                self.playerturn(player)
                self.displaystate(display, delay, pause)

                if len(player.hand.cards) < 1:
                    self.winner = player.name
                    return player.name 
                    
                player.hand.flip()
        return None

    # ------------------------------------------------------------------
    def playerturn(self, player):
        hand = player.hand
        elected = self.choosecard(hand)
        if elected == None:
            # No playable card, must draw
            hand.cards.append(self.drawcard())
        else:
            # Play elected card on top of discard pile
            hand.cards.remove(elected)
            self.discard.cards.append(elected)

            # If a crazy 8 was selected, choose next suit
            if elected.rank == self.CRAZY8 and len(hand.cards) > 0:
                self.next_suit = hand.top().suit
            else:
                self.next_suit = self.discard.top().suit
        # Next rank always from top card
        self.next_rank = self.discard.top().rank 
 
    # ------------------------------------------------------------------
    def choosecard(self, hand):
        # Trivial choice: last valid card in hand
        candidates = [
            card for card in hand.cards 
                if card.rank == self.CRAZY8 \
                   or card.suit == self.next_suit \
                   or card.rank == self.next_rank
        ]
        return candidates[-1] if len(candidates) > 0 else None

    # ------------------------------------------------------------------
    def drawcard(self):
        # If deck is empty, leave top card in discard pile and
        # reshuffle the rest as new drawing deck
        if len(self.deck.cards) < 1:
            self.deck = self.discard
            self.discard = self.deck.deal(1,facedown=False)
            self.deck.flip()
            self.deck.shuffle()
        return self.deck.draw(facedown=False)

    # ------------------------------------------------------------------
    def displaystate(self, display=True, delay=0, pause=False):
        if display:
            os.system("clear")
            print(self.title)
            print("\nTurn {:03}".format(self.turn))
            for player in self.players:
                print("\n{}: {}".format(player.name, player.hand))
            print("\nDiscard: ", self.discard)
            print("\nDeck: ", self.deck)
            if self.next_rank == self.CRAZY8:
                print("\nCRAZY 8 played. Next suit is", self.next_suit)
            if self.winner != None:
                print("\nWinner is", self.winner)
            time.sleep(delay)
            if pause:
                input("\nEnter to continue...")
    
    # ------------------------------------------------------------------
    def cleanup(self):
        for player in self.players:
            player.hand.facedown(False)
        
# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------

if __name__ == "__main__":
    game = Crazy8s(players=3)
    winner = game.play(display=False, delay=0.0, pause=False)
    game.cleanup()
    while True:
        game.displaystate(pause=False)
        if input("\nq to exit ") == "q":
            break

