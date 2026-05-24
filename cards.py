# ----------------------------------------------------------------------
# cards.py v1.3
# Classes for card-games
#
# v1.1
# > CardStack is now iterable
# > Add suits method to CardStack
# > Add ranks method to CardStack
# > Add search method to CardStack
# > Add __contains__, __getitem__ methods to CardStack
# > shuffle and facedown optargs in FrenchDeck.create()
# > Augment flip in CardStack: Can flip stack as a solid unit,
#   effectively reversing it
#
# v1.2
# > Add fields for image data in Cards class
#
# v1.3
# > Static method to load images from disk in FrenchDeck class
# > Include card name property in Cards class
# > Facedown revision: keep the present value when arg is None
# > Change front and back from Card class into properties with seek(0)
# ----------------------------------------------------------------------


from random import shuffle
from io import BytesIO


# ----------------------------------------------------------------------
class Card:
    """ Class for suit/value cards """

    # ------------------------------------------------------------------
    def __init__(self, suit, rank, symbol,
                 facedown=False, fdsymbol=chr(0x1F0A0),
                 front=None, back=None):
        self.suit = suit
        self.rank = rank
        self.symbol = symbol
        self.facedown = facedown
        self.fdsymbol = fdsymbol
        self._front = front
        self._back = back

    # ------------------------------------------------------------------
    @property
    def front(self):
        """ Front in-memory image, needs seek before every access """
        try:
            self._front.seek(0)
        finally:
            return self._front

    # ------------------------------------------------------------------
    @property
    def back(self):
        """ Back in-memory image, needs seek before every access """
        try:
            self._back.seek(0)
        finally:
            return self._back

    # ------------------------------------------------------------------
    def __repr__(self):
        return str(self.symbol if not self.facedown else self.fdsymbol)\
                + ' '

    # ------------------------------------------------------------------
    def flip(self):
        """ Flip card """
        self.facedown = not self.facedown

    # ------------------------------------------------------------------
    @property
    def name(self):
        return self.rank + ' of ' + self.suit


# ----------------------------------------------------------------------
class CardStack:
    """ A stack of Card objects. """
    # todo: List container, maybe inherit from list in future versions

    # ------------------------------------------------------------------
    def __init__(self, cards=[], shuffle=False, facedown=None):
        self.cards = list(cards)
        if shuffle:
            self.shuffle()
        if facedown is not None:
            self.facedown(facedown=facedown)

    # ------------------------------------------------------------------
    def __repr__(self):
        return ''.join([str(card) for card in self.cards])

    # ------------------------------------------------------------------
    def __len__(self):
        return len(self.cards)

    # ------------------------------------------------------------------
    def __iter__(self):
        """ Make this class iterable """
        for card in self.cards:
            yield card

    # ------------------------------------------------------------------
    def __getitem__(self, item):
        """ Support slicing in this container class """
        return self.cards[item]

    # ------------------------------------------------------------------
    def __contains__(self, item):
        """ Check inclusion by suit, rank or card """
        return item in self.suits() \
                or item in self.ranks() \
                or item in self.cards

    # ------------------------------------------------------------------
    def shuffle(self):
        """ Randomly shuffle cards in the stack """
        shuffle(self.cards)

    # ------------------------------------------------------------------
    def facedown(self, facedown=True):
        """ Set facing of every card in stack """
        if facedown is not None:
            for card in self.cards:
                card.facedown = facedown

    # ------------------------------------------------------------------
    def flip(self, reverse=False):
        """ Flip cards in stack individually or as a whole """
        for card in self:
            card.flip()
        if reverse:
            self.cards.reverse()

    # ------------------------------------------------------------------
    def deal(self, count, facedown=None):
        """ Get cards from stack, return them as new stack """
        cards = []
        for numcards in range(count):
            card = self.draw(facedown=facedown)
            if card is None:
                break
            else:
                cards.append(card)
        return CardStack(cards, facedown=facedown)

    # ------------------------------------------------------------------
    def draw(self, facedown=None):
        """ Draw top card and return it if available """
        if self.top() is None:
            card = None
        else:
            card = self.cards.pop()
            if facedown is not None:
                card.facedown = facedown
        return card

    # ------------------------------------------------------------------
    def top(self):
        """ Peek at top card """
        return self.cards[-1] if len(self.cards) > 0 else None

    # ------------------------------------------------------------------
    def search(self, ranks=[], suits=[], cards=[], negate=False):
        """ Search cards in stack, return matches as card generator """

        R, S, C = set(ranks), set(suits), set(cards)
        for card in self:
            match = card.rank in R or card.suit in S or card in C
            if (match and not negate) or (not match and negate):
                yield card

    # ------------------------------------------------------------------
    def suits(self):
        """ Generator for suit of cards in stack """
        for card in self:
            yield card.suit

    # ------------------------------------------------------------------
    def ranks(self):
        """ Generator for rank of cards in stack """
        for card in self:
            yield card.rank


# ----------------------------------------------------------------------
class FrenchDeck:
    """ Abstract class for a standard french deck """

    SUITS = ('SPADES', 'HEARTS', 'DIAMONDS', 'CLUBS')
    RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10',
             'J', 'Q', 'K')

    # ------------------------------------------------------------------
    @staticmethod
    def create(shuffle=False, facedown=False):
        """
        Static method for deck creation
        Returns a list of Card objects
        """
        # Unicode symbol table for french cards start at 0X1F0A1
        # each set has 15 cards, hence the 16 offset for each suit
        # Ignore card symbol for Knight, unused in the french deck
        # Knight is located at offset 11, between Jack and Queen.
        cards = [Card(suit, rank, chr(0X1F0A1 + 16*s + r + r//11))
                        for s, suit in enumerate(FrenchDeck.SUITS)
                        for r, rank in enumerate(FrenchDeck.RANKS)
        ]
        return CardStack(cards=cards,
                         shuffle=shuffle, facedown=facedown)

    # ------------------------------------------------------------------
    @staticmethod
    def loadimages(card_stack, dirname='./', ext='.png', back='back'):
        """ Static method to load image data into a stack of cards """

        try:
            with open(dirname + back + ext, 'rb') as backfile:
                back_image = BytesIO(backfile.read())
            for card in card_stack:
                filename = card.name.lower().replace(' ', '_')
                with open(dirname + filename + ext, 'rb') as frontfile:
                    card._front = BytesIO(frontfile.read())
                    card._back = back_image
        except FileNotFoundError:
            print('File error. Card images not loaded.')
            raise
        except (TypeError, AttributeError):
            print('Type/Attribute error. Card images not loaded.')
            raise


# ----------------------------------------------------------------------
# Main segment for testing purposes
# ----------------------------------------------------------------------
if __name__ == '__main__':
    from PIL import Image

    deck = FrenchDeck.create()
    FrenchDeck.loadimages(deck, dirname='./img/')
    for i, card in enumerate(deck[0:5]):
        print('{:2}: {} ({})'.format(i+1, card, card.name))
        if card.front is not None:
            Image.open(card.front).show()
