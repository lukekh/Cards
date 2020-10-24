import random

# Global variables
s_map = {
    'spade': 0, 'spades': 0, 's': 0, u'\u2660': 0, 0: 0, '0': 0,
    'heart': 1, 'hearts': 1, 'h': 1, u'\u2661': 1, 1: 1, '1': 1,
    'diamond': 2, 'diamonds': 2, 'd': 2, u'\u2662': 2, 2: 2, '2': 2,
    'club': 3, 'clubs': 3, 'c': 3, u'\u2663': 3, 3: 3, '3': 3
}
p_map = {
    **dict(zip(range(2, 15), range(2, 15))),
    **dict(zip([str(i) for i in range(2, 15)], range(2, 15))),
    **{
        'j': 11, 'jack': 11,
        'q': 12, 'queen': 12,
        'k': 13, 'king': 13,
        'a': 14, 'ace': 14, 1: 14, '1': 14  # This bit means Aces are high
    }
}


class Card:
    def __init__(self, pip, suit, display_pip="letter", display_suit="unicode"):
        """
        A playing card.

        Aces always mapped to pip==14.
        Use set_option to change default display options.

        :param pip: str or int; the rank of the card
        :param suit: str; the suit of the card
        :param display_pip: str; default="letter"; user setting for default repr and str of pip value
        :param display_suit: str; default="unicode"; user setting for default repr and str of suit value
        """
        if str(pip).lower() in p_map:
            self.pip = p_map[str(pip).lower()]
        else:
            self.pip = int(pip)

        if self.pip > 14:
            raise TypeError("a Card type must have a pip less than 15.")
        self.suit = s_map[str(suit).lower()]

        self.suit_opts = {'unicode': {0: u'\u2660', 1: u'\u2661', 2: u'\u2662', 3: u'\u2663'},
                          'letter': {0: 'S', 1: 'H', 2: 'D', 3: 'C'},
                          'word': {0: 'Spades', 1: 'Spades'}
                          }

        nums = dict(zip(range(2, 11), [str(n) for n in range(2, 11)]))
        self.pip_opts = {'letter': {**nums, **{11: 'J', 12: 'Q', 13: 'K', 14: 'A'}},
                         'word': {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                                  9: "Nine",
                                  10: "Ten", 11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}
                         }

        self.display_pip, self.display_suit = None, None  # Initialise before setting
        self.set_option(display_suit=display_suit, display_pip=display_pip)

    def set_option(self, **kwargs):
        """
        This method sets the default display options
        """
        handles = ("display_pip", "display_suit")

        for key in kwargs:
            if key not in handles:
                raise TypeError(f'"{key}" is not a valid option to set. You can use set options to change '
                                f'{", ".join(handles[:-1])} or {handles[-1]}.')

        if "display_pip" in kwargs:
            if str(kwargs["display_pip"]).lower() in self.pip_opts:
                self.display_pip = str(kwargs["display_pip"]).lower()
            else:
                raise TypeError(
                    f'"{kwargs["display_pip"]}" is not a valid display_pip option. Try using '
                    f'{", ".join(list(self.pip_opts)[:-1])} or {list(self.pip_opts)[-1]}.'
                )

        if "display_suit" in kwargs:
            if str(kwargs["display_suit"]).lower() in self.suit_opts:
                self.display_suit = str(kwargs["display_suit"]).lower()
            else:
                raise TypeError(
                    f'"{kwargs["display_suit"]}" is not a valid display_suit option. Try using '
                    f'{", ".join(list(self.suit_opts)[:-1])} or {list(self.suit_opts)[-1]}.'
                )

    def __str__(self):
        if (self.display_pip == "word") or (self.display_suit == "word"):
            return f'{self.pip_opts[self.display_pip][self.pip]} of {self.suit_opts[self.display_suit][self.suit]}'
        else:
            return self.pip_opts[self.display_pip][self.pip] + self.suit_opts[self.display_suit][self.suit]

    def __repr__(self):
        return str((self.pip_opts[self.display_pip][self.pip], self.suit_opts[self.display_suit][self.suit]))

    def __eq__(self, other):
        if isinstance(other, Card):
            return (self.pip == other.pip) and (self.suit == other.suit)
        else:
            return False

    def __le__(self, other):
        if isinstance(other, Card):
            return self.pip <= other.pip
        else:
            return self.pip <= other

    def __lt__(self, other):
        if isinstance(other, Card):
            return self.pip < other.pip
        else:
            return self.pip < other

    def __hash__(self):
        return hash((self.pip, self.suit, type(self).__name__))


# A class that simulates a hand of cards. Kept general to be used as a parent class for specific games.
class Hand:
    """
    A hand of cards.

    This class takes in Card arguments and stores them as a list
    :param args: Card; the Cards that constitute the Hand
    """
    def __init__(self, *args):
        self.cards = [card for card in args if isinstance(card, Card)]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str([str(card) for card in self])

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return self.cards.__iter__()

    @classmethod
    def subset(cls, *args):
        return cls(*args)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.subset(*self.cards.__getitem__(item))
        else:
            return self.cards.__getitem__(item)

    def suit(self, suit):
        return self.subset(*[card for card in self if card.suit == s_map[suit]])

    def pip(self, pip):
        return self.subset(*[card for card in self if card.pip == p_map[pip]])

    def append(self, item):
        if isinstance(item, Card):
            self.cards.append(item)
        else:
            raise TypeError(f'can only append Card (not "{type(item).__name__}") to {type(self).__name__}')

    def __add__(self, other):
        try:
            return self.subset(*(self.cards + other.cards))
        except TypeError:
            raise TypeError(f'can only concatenate Hand or subclass of Hand (not "{type(other).__name__}" to '
                            f'{type(self).__name__}')

    def sorted(self, reverse=True):
        temp = self.cards
        temp.sort(reverse=reverse)
        return self.subset(*temp)

    def __bool__(self):
        return bool(self.cards)


class Deck:
    """
    A deck of cards.

    This is a standard 52 cards deck. Jokers not included.
    Use kwarg card to make your own custom deck.

    :param cards: list; a list of cards to form a custom deck - if None, will generate a standard deck
    :param decks: int; the number of decks
    :param shuffled: bool; whether or not you want the deck shuffled
    """
    def __init__(self, cards:list = None, decks:int = 1, shuffled:bool = True):
        if cards is None:
            self.cards = [Card(pip, suit) for pip in range(2, 15) for suit in ('S', 'H', 'D', 'C')] * decks
        else:
            self.cards = cards * decks

        if shuffled:
            random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def __add__(self, other):
        try:
            return Deck(cards=self.cards + other.cards)
        except TypeError:
            raise TypeError(f'can only concatenate Deck (not "{type(other).__name__}" to '
                            f'{type(self).__name__}')

    def __mul__(self, other):
        return Deck(cards=self.cards * other)

    def __getitem__(self, item):
        return self.cards[item]

    def __delitem__(self, key):
        del self.cards[key]

    def __str__(self):
        return r"Deck{" + f"{len(self)} cards" + r"}"

    def __repr__(self):
        return str(self)

    def reveal(self, n=5):
        """
        return a
        """
        return r"Deck{" + f"{', '.join([str(card) for card in self.cards[:n]] + ['...'])}" + r"}"

    def append(self, item):
        if isinstance(item, Card):
            self.cards.append(item)
        else:
            raise TypeError(f'can only append Card (not "{type(item).__name__}") to {type(self).__name__}')

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, *hands, cards=1, burn=False, discards=None):
        if burn:
            if discards is not None:
                discards.append(self[0])
            del self[0]
        for i in range(cards):
            for hand in hands:
                hand.append(self[0])
                del self[0]


if __name__ == "__main__":
    h1 = Hand()
    h2 = Hand()

    d = Deck()

    d.deal(h1, h2, cards=2)

    print(h1, h2)
