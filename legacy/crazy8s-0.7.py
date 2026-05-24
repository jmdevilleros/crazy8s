# ----------------------------------------------------------------------
# crazy8s-0.7.py
# Crazy Eights
# ----------------------------------------------------------------------


from cards import FrenchDeck # uses v1.0
from os import system
from time import sleep 
from random import choice 


# ----------------------------------------------------------------------

class Crazy8s():
    """ Container class for crazy 8s game """

    CRAZY8 = "8"
    MAXPLAYERS = 10
    
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
        self.deck.facedown()
        self.deck.shuffle()
        self.players = self.setplayers(players)
        self.discard = self.deck.deal(1, facedown=False)
        self.next_suit = self.discard.top().suit
        self.next_rank = self.discard.top().rank
        self.winner = None
        self.crazyplayer = None
        self.turn = 0
        self.reshuffles = 0
        self.emptydraws = 0
    
    # ------------------------------------------------------------------    
    def setplayers(self, numplayers):
        """ Assign name to players, deal cards and define play order """
        handsize = 7 if numplayers < 3 else 5
        players = [
            self.Player("Player{:02}".format(player + 1), 
                        self.deck.deal(handsize, facedown=True))
            for player in range(min(numplayers,self.MAXPLAYERS))
        ]
        firstplayer = choice(players)
        index = players.index(firstplayer)
        players = players[index:] + players[:index]
        return players
               
    # ------------------------------------------------------------------                
    def play(self, display=True, delay=0, pause=True):
        """ Game loop """
        while self.winner == None:
            self.turn += 1
            for player in self.players:
                player.hand.flip()
                self.displaystate(display, delay, pause)
                self.playerturn(player)
                player.hand.flip()
                if len(player.hand) < 1:
                    self.winner = player
                    break
        return self.winner

    # ------------------------------------------------------------------
    def playerturn(self, player):
        """ Execute actions in player's turn """
        hand = player.hand
        elected = self.choosecard(hand)
        if elected == None:
            # No playable card, must draw
            draw = self.drawcard()
            # If deck is empty, skip
            if draw != None:
                hand.cards.append(draw)
        else:
            # Play elected card on top of discard pile
            hand.cards.remove(elected)
            self.discard.cards.append(elected)

            # If a crazy 8 was selected, choose next suit
            if elected.rank == self.CRAZY8 and len(hand) > 0:
                self.crazyplayer = player
                self.next_suit = hand.top().suit
            else:
                self.next_suit = self.discard.top().suit
        # Next rank always from top card
        self.next_rank = self.discard.top().rank 
 
    # ------------------------------------------------------------------
    def choosecard(self, hand):
        """ Select which card to play """
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
        """ Special drawing: may reshuffle """
        # If deck is empty, leave top card in discard pile and
        # reshuffle the rest as new drawing deck
        if len(self.deck) < 1:
            self.deck = self.discard
            self.discard = self.deck.deal(1,facedown=False)
            self.deck.flip()
            self.deck.shuffle()
            self.reshuffles += 1
        # Deck empty again, return no card
        if len(self.deck) < 1:
            self.emptydraws += 1
            return None
        else:
            return self.deck.draw(facedown=False)

    # ------------------------------------------------------------------
    def displaystate(self, display=True, delay=0, pause=False):
        """ Show game data """
        if display:
            system("clear")
            print(self.title)
            print("\nTurn {:03}".format(self.turn))
            for player in self.players:
                print("\n{}: {}".format(player.name, player.hand))
            print("\nDiscard: ", self.discard)
            print("\nDeck:    ", self.deck)
            if self.next_rank == self.CRAZY8 and self.turn > 1:
                print("\nCRAZY 8 played by {}. Next suit is {}".format(
                        self.crazyplayer.name, self.next_suit))
            if self.winner != None:
                print("\nWinner is", self.winner.name)
            sleep(delay)
            if pause:
                input("\nEnter to continue...")
    
    # ------------------------------------------------------------------
    def reveal(self):
        """ Reveal everything """
        self.deck.facedown(False)
        self.discard.facedown(False)
        for player in self.players:
            player.hand.facedown(False)


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------

if __name__ == "__main__":
    game = Crazy8s(players=5)
    winner = game.play(display=True, delay=0.0, pause=True)
    game.reveal()
    while True:
        game.displaystate(pause=False)
        if input("\nq to exit ") == "q":
            break

