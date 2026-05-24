# ----------------------------------------------------------------------
# crazy8s-0.8.py
# Crazy Eights
# ----------------------------------------------------------------------


from cardgames import CardGame
from players import Player
from cards import FrenchDeck
from os import system


# ----------------------------------------------------------------------
class Crazy8s(CardGame):
    """ Container class for crazy 8s game """

    CRAZY8 = "8"
    MAXPLAYERS = 10
    MAXROUNDS = 300

    # ------------------------------------------------------------------
    def initialize(self):
        """ Game inizialization """
        
        # Invoke super class initialization
        super().initialize()

        self.crazy_player = None
        self.reshuffles = 0
        self.emptydraws = 0
        
        # Prepare drawing deck    
        self.drawing = FrenchDeck.create()
        self.drawing.facedown()
        self.drawing.shuffle()
            
        # Deal hands 
        handsize = 7 if len(self.players) < 3 else 5
        for player in self.players:
            player.data = self.drawing.deal(
                min(handsize, len(self.drawing)), facedown=True)
                
        # Prepare discard pile
        self.discard = self.drawing.deal(1, facedown=False)
        self.next_suit = self.discard.top().suit
        self.next_rank = self.discard.top().rank

    # ------------------------------------------------------------------
    def playturn(self):
        """ Turn actions """
        
        hand = self.current_player.data
        
        # Find possible cards to play
        candidates = [
            card for card in hand.cards 
                if card.rank == self.CRAZY8 \
                   or card.suit == self.next_suit \
                   or card.rank == self.next_rank
        ]
        
        # Select card to play if available
        elected = candidates[-1] if len(candidates) > 0 else None
        if elected != None:
            # Play the card
            elected.flip()
            hand.cards.remove(elected)
            self.discard.cards.append(elected)
            if elected.rank == self.CRAZY8 and len(hand) > 0:
                # If a crazy 8 was played, select next suit
                self.next_suit = hand.top().suit
                self.crazy_player = self.current_player
            else:
                self.next_suit = self.discard.top().suit
        else:
            # No card to play
            if len(self.drawing) < 1 and len(self.discard) > 1:
                # Attempt a reshuffle from discard if deck is emtpy
                self.drawing = self.discard
                self.discard = self.drawing.deal(1)
                self.drawing.flip()
                self.drawing.shuffle()
                self.reshuffles += 1
            if len(self.drawing) > 0:
                # If deck is not empty, draw
                hand.cards.append(self.drawing.draw())
            else:
                self.emptydraws += 1

        # Next rank always from top, even if crazy 8 was played
        self.next_rank = self.discard.top().rank 
        
    # ------------------------------------------------------------------
    def is_running(self):
        """ Determine if game shall stop or continue """
        
        running = True
        if self.current_player == None:
            running = True
        elif len(self.current_player.data.cards) < 1:
            self.winner = self.current_player
            running = False
        return running and self.current_round < self.MAXROUNDS

    # ------------------------------------------------------------------
    def displaystate(self, display=True, pause=False):
        """ Show game data """

        if display:
            self.current_player.data.flip()
            system("clear")
            print(self.title)
            print("\nRound {:03}".format(self.current_round))
            print("Turn {:04}".format(self.current_turn))
            for player in self.players:
                print("\n {} {:8}:{}".format(
                        ">>" if player == self.current_player else "  ",
                        player.name, 
                        player.data))
            print("\nDiscard: ", self.discard)
            print("\nDrawing: ", self.drawing)
            if self.next_rank == self.CRAZY8:
                print("\nCRAZY 8 played by {}. Next suit is {}".format(
                        self.crazy_player.name \
                            if self.crazy_player != None
                            else "drawing",
                        self.next_suit))
            if self.winner != None:
                print("\nWinner is", self.winner.name)
            if pause:
                input("\nEnter to continue...")
            self.current_player.data.flip()
            
    # ------------------------------------------------------------------
    def finish(self):
        """ Reveal everything at game end """
        
        self.drawing.flip()
        for player in self.players:
            player.data.flip()
            
# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------

if __name__ == "__main__":
    
    game = Crazy8s(title="Crazy 8s", players=Player.createlist(10))
    game.play(display=True, delay=0, pause=True)

    while True:
        game.displaystate(pause=False)
        if input("\nq to exit ") == "q":
            break

