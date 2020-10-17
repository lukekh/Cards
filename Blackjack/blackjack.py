"""
This module simulates Blackjack
"""

import Cards


class Card(Cards.Card):
    """
    A playing card in blackjack.

    Child of Cards.Card, adds method value for blackjack hand evaluation.
    """
    def value(self):
        """
        The value of a card in a blackjack deal.

        Aces will evaluate to 11 and the Blackjack.Hand class will figure out if they need to be soft.
        :return: int; value
        """
        if self.pip == 14:
            return 11
        else:
            return min(self.pip, 10)


class Hand(Cards.Hand):
    """
    A hand of cards in blackjack.

    Child of Cards.Hand, adds method value for blackjack hand evaluation.
    """
    def sorted(self, **kwargs):
        raise NotImplementedError("It is important to preserve the deal order in Blackjack.")

    def value(self):
        """
        evaluate a blackjack hand
        :return: int; current value of hand
        """
        val = sum([card.value() for card in self])

        # if hand is soft, alter to be below 21 if possible
        aces = len(self.pip('ace'))
        val -= 10*min(aces, 1 + (val-22)//10)
        return val


class Dealer:
    """
    A blackjack dealer.

    Encode the behaviour of a blackjack dealer.
    """
    def __init__(self):
        self.hand = Hand()

    def hit_me(self):
        """
        dealer wants an extra card
        """
        # TODO: Add hit me logic
        pass

    def resolve(self):
        """
        resolve the dealers betting round
        """
        while self.hand.value() < 17:
            self.hit_me()

    def reset(self):
        """
        reset the state of the dealer to have no cards
        """
        self.hand = Hand()


class Table:
    """
    A blackjack table.

    :param decks: int; the number of decks
    """
    def __init__(self, decks: int = 6):
        self.dealer = Dealer()
        self.shoe = Cards.Deck(decks=decks, shuffled=True)


