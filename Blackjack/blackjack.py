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
    A blackjack table with a single player and a dealer.

    :param decks: int; the number of decks
    :param chips: int; the number of chips the player has for betting
    """
    def __init__(self, decks: int = 6, chips: int = 100):
        self.dealer = Dealer()
        self.shoe = Cards.Deck(decks=decks, shuffled=True)
        self.discards = Cards.Deck(cards=[])
        self.player = Hand()
        self.chips = chips

    def deal(self):
        """
        Initial deal.
        """
        # First, burn a card
        self.shoe.deal(cards=0, burn=True)
        # Deal to the player first, then the dealer
        self.shoe.deal(self.player, self.dealer, cards=2, discards=self.discards)

    def round(self):
        pass

    def end_hand(self):
        """
        Clean up cards at the end of a hand.
        """
        self.discards += self.dealer + self.player
        self.dealer = Hand()
        self.player = Hand()


def options(hand: Hand):
    """
    Find the options a player has given a blackjack hand.

    :param hand: Hand; the hand a player is considering
    :return: dictionary containing options
    """
    # Initialise dictionary
    # The player can always stand
    options_dict = {'stand': True}

    # Can the player hit?
    if hand.value() > 21:
        options_dict['hit'] = False
    else:
        options_dict['hit'] = True

    # Can the player split?
    # Check player has only their first two cards and both have the same value
    if (len(hand) == 2) and (set([card.value() for card in hand]) == 1):
        options_dict['split'] = True
    else:
        options_dict['split'] = False

    #return options
    return options_dict



if __name__ == "__main__":
    pass
