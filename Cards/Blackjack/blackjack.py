"""
This module simulates Blackjack
"""
import random
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
        # Not certain if I want to keep aces evaluating to 14
        if self.pip in (1, 14):
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
        val -= 10*min(aces, 1 + max(val - 22, 0)//10)
        return val

    def blackjack(self):
        """
        Figure out if the hand is blackjack.

        :return: bool; whether the hand is blackjack
        """
        return True if (len(self) == 2) and (self.value() == 21) else False


class Shoe(Cards.Deck):
    """
    The same as a deck, it just requires blackjack cards
    """
    def __init__(self, cards:list = None, decks:int = 1, shuffled:bool = True):
        if cards is None:
            self.cards = [Card(pip, suit) for pip in range(2, 14) for suit in ('S', 'H', 'D', 'C')] * decks
        else:
            self.cards = cards * decks

        if shuffled:
            random.shuffle(self.cards)


class Dealer:
    """
    A blackjack dealer.

    Encode the behaviour of a blackjack dealer.
    """
    def __init__(self):
        self.hand = Hand()

    def value(self):
        return self.hand.value()

    def print_hidden(self):
        return f"{self.hand[0]}, ??"

    def print_reveal(self):
        return ", ".join([str(card) for card in self.hand])

    def hit_me(self, table):
        """
        dealer wants an extra card
        """
        table.deal(self.hand)

    def resolve(self, table):
        """
        resolve the dealers betting round
        """
        while self.value() < 17:
            self.hit_me(table)

    def reset(self, discards=None):
        """
        reset the state of the dealer to have no cards
        """
        if discards is not None:
            discards += self.hand
        self.hand = Hand()


class Table:
    """
    A blackjack table with a single player and a dealer.

    :param decks: int; the number of decks
    :param chips: int; the number of chips the player has for betting
    """
    def __init__(self, decks: int = 6, chips: int = 100):
        self.dealer = Dealer()
        self.shoe = Shoe(decks=decks, shuffled=True)
        self.discards = Shoe(cards=[])
        self.player = Hand()
        self.chips = chips
        self.bet = 0

    def deal(self, hand):
        """
        Deal one card to a hand, no burn
        """
        self.shoe.deal(hand)

    def initial_deal(self):
        """
        Initial deal.
        """
        # First, burn a card
        self.shoe.deal(cards=0, burn=True, discards=self.discards)
        # Deal to the player first, then the dealer
        self.shoe.deal(self.player, self.dealer.hand, cards=2, discards=self.discards)

    def round(self):
        """
        Playing a round
        """
        def make_choice(cards, dealer, bet, stack):
            options = generate_options(cards, bet, stack)
            print(f"Dealer shows: {dealer.print_hidden()}")
            print(f"You're dealt: {', '.join([str(card) for card in cards])}")
            print(f"Current bet: {bet}, Current stack: {stack}")
            print(f"Your options: {', '.join([option for option in options])}\n")
            player_choice = input("Choose option: ").lower()
            if player_choice in options:
                return player_choice
            else:
                print("Your option was invalid, please try again.\n")
                return make_choice(cards, dealer, bet, stack)

        def action(player_choice, shoe, cards, bet):
            """
            refer to generate_options for list of possible options

            current supported options are hit and double
            (stand causes loop to break before this function is called and split is dealt with separately)
            """
            if player_choice == 'hit':
                shoe.deal(cards)
            elif player_choice == 'double':
                shoe.deal(cards)

        print(f"You have {self.chips} chip{'s'*(self.chips > 1)}.")
        self.bet = input("How much would you like to bet?: ")

        try:
            assert float(self.bet) == abs(int(self.bet))
        except AssertionError:
            print("Your bet must be a positive whole number")
            return
        except ValueError:
            print("Your bet must be valid integer")
            return
        except Exception as e:
            print(f"{e} - I'm going to have to ask you to leave, sir")
            return

        self.bet = int(self.bet)

        if self.bet > self.chips:
            print("You do not have enough chips.")
            # End round
            return

        self.chips -= self.bet

        def play_hand(dealer, shoe, hand, bet, stack, hands):
            if not dealer.hand.blackjack():
                while hand.value() <= 21:
                    choice = make_choice(hand, dealer, bet, stack)
                    if choice == 'split':
                        self.chips -= self.bet
                        h1 = Hand(hand[0])
                        shoe.deal(h1)
                        play_hand(dealer, shoe, h1, bet, stack, hands)
                        h2 = Hand(hand[1])
                        shoe.deal(h2)
                        play_hand(dealer, shoe, h2, bet, stack, hands)
                        return hands
                    elif choice == 'double':
                        self.chips -= self.bet
                        self.bet *= 2
                    action(choice, shoe, hand, bet)
                    if choice == "stand":
                        break
            hands.append(hand)
            return hands

        all_hands = play_hand(self.dealer, self.shoe, self.player, self.bet, self.chips, [])

        self.dealer.resolve(self)

        # Print results
        print(f"Dealer shows: {self.dealer.print_reveal()}")
        for hand in all_hands:
            print(f"Player shows: {', '.join([str(card) for card in hand])}")
            if self.dealer.hand.blackjack():
                print(f"Dealer has blackjack. House wins.")
            if hand.blackjack():
                print(f"Player has blackjack and wins {int(self.bet * 1.5)} chip{'s'*(self.chips > 1)}.")
                self.chips += int(self.bet * 2.5)
            elif hand.value() > 21:
                print("Player busts.")
            elif self.dealer.value() > 21:
                print(f"Dealer busts. Player wins {int(self.bet)} chip{'s'*(self.chips > 1)}.")
                self.chips += 2*self.bet
            elif self.dealer.value() < hand.value():
                print(f"Player wins {int(self.bet)} chip{'s'*(self.chips > 1)}.")
                self.chips += 2*self.bet
            elif self.dealer.value() >= hand.value():
                print("House wins.")
            else:
                print("Something strange has happened.")

        self.end_hand()

    def end_hand(self):
        """
        Clean up cards at the end of a hand.
        """
        self.discards += self.dealer.hand + self.player
        self.dealer.reset(self.discards)
        self.player = Hand()
        self.bet = 0
        if 3*len(self.discards) > len(self.shoe):
            self.shoe = self.shoe + self.discards
            self.shoe.shuffle()

    def play(self):
        starting_chips = self.chips
        while self.chips > 0:
            self.end_hand()
            self.initial_deal()
            self.round()
            if self.chips > 0:
                play_again = input(f"\nYou have {self.chips} chip{'s'*(self.chips > 1)}. Play again?\n")
            else:
                play_again = 'no'
            if play_again.lower() in ('no', 'n', 'false', 'f'):
                break
        winnings = self.chips - starting_chips
        if winnings > 0:
            print(f"Winner winner chicken dinner - you won {winnings} chip{'s'*(self.chips > 1)}.")
        if winnings == 0:
            print("You broke even.")
        else:
            print(f"The house always wins - you lost {-winnings} chip{'s'*(self.chips > 1)}.")


def generate_options(hand: Hand, bet: int, stack: int) -> dict:
    """
    Find the options a player has given a blackjack hand.

    :param hand: Hand; the hand a player is considering
    :param bet: int; the bet the player has put down on the table
    :param stack: int; the amount of money the player has
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
    # Check player can double their bet, has only their first two cards and both have the same value
    if (bet <= stack) and (len(hand) == 2) and (len(set([card.value() for card in hand])) == 1):
        options_dict['split'] = True
    else:
        options_dict['split'] = False

    # Can the player double?
    # Check player has enough money left to double their bet
    if (bet <= stack) and (len(hand) == 2):
        options_dict['double'] = True
    else:
        options_dict['double'] = False

    options = [option for option in options_dict if options_dict[option]]

    return options


def play_blackjack(chips=100):
    t = Table(chips=chips)
    t.play()


if __name__ == "__main__":
    play_blackjack()
