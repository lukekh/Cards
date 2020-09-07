import Cards
import random


class TableError(Exception):
    """"
    This special exception can be used to better handle Poker.Table errors
    """
    pass


poker_ranks = {
    "null": 0,
    "high card": 1,
    "pair": 2,
    "two pair": 3,
    "three of a kind": 4,
    "straight": 5,
    "flush": 6,
    "full house": 7,
    "four of a kind": 8,
    "straight flush": 9,
    "royal flush": 10
}


# Will be resolved as Poker.Hand
class Hand(Cards.Hand):
    def straight(self):
        """
        Finds the highest valued straight in a collection of cards
        :return: Hand; the highest straight, empty hand if no straight
        """
        for i in reversed(range(5, 15)):  # This makes sure we don't check for an impossible straight
            counter = 0
            consecutive = Hand()
            while len(consecutive) < 5:
                if self.pip(i - counter):  # Are there any cards with this pip, counting backward via counter
                    consecutive.append(self.pip(i - counter)[0])
                    counter += 1
                else:
                    break
            if len(consecutive) > 4:
                return consecutive
        return Hand()  # Empty if there is no straight

    def full_house(self):
        """
        Finds the highest valued full house in a collection of cards
        :return: Hand; the highest full house, empty hand if no straight
        """
        pips = [len(self.pip(i)) for i in range(2, 15)]
        pips_and_pips = [(pips[i], pips[:i] + [0] + pips[i + 1:]) for i, _ in enumerate(pips)]

        for i, (pip_count, other_pip_counts) in enumerate(reversed(pips_and_pips)):
            if pip_count > 2:
                pip_temp = self.pip(14 - i) if len(self.pip(14 - i)) == 3 else self.pip(14 - i)[0:3]
                for j, other_pip_count in enumerate(reversed(other_pip_counts)):
                    if other_pip_count > 1:
                        other_pip_temp = self.pip(14 - j) if len(self.pip(14 - j)) == 2 else self.pip(14 - j)[0:2]
                        return pip_temp + other_pip_temp
        return Hand()

    def two_pair(self):
        """
        Finds the highest valued two pair in a collection of cards
        :return: Hand; the highest two pair + kicker, empty hand if no straight
        """
        pips = [len(self.pip(i)) for i in range(2, 15)]
        pips_and_pips = [(pips[i], pips[:i] + [0] + pips[i + 1:]) for i, _ in enumerate(pips)]

        for i, (pip_count, other_pip_counts) in enumerate(reversed(pips_and_pips)):
            if pip_count > 1:
                pip_temp = self.pip(14 - i) if len(self.pip(14 - i)) == 2 else self.pip(14 - i)[0:2]
                for j, other_pip_count in enumerate(reversed(other_pip_counts)):
                    if other_pip_count > 1:
                        other_pip_temp = self.pip(14 - j) if len(self.pip(14 - j)) == 2 else self.pip(
                            14 - j)[0:2]
                        return pip_temp + other_pip_temp + Hand(
                            max([card for card in self if card not in (pip_temp + other_pip_temp)]))
        return Hand()

    def val(self):

        if len(self) == 0:
            return "null", Hand()

        # Count
        suit_count = [len(self.suit(i)) for i in range(4)]
        pip_count = [len(self.pip(i)) for i in range(2, 15)]
        pip_sort = pip_count.copy()
        pip_sort.sort(reverse=True)
        max_pips = pip_sort[0:2]

        if max(suit_count) >= 5:
            straight_flushes = []
            flushes = []
            for i, count in enumerate(suit_count):
                if count >= 5:
                    if self.suit(i).straight():
                        s = self.suit(i).straight()
                        if s.pip(14) + s.pip(13):
                            return "royal flush", s
                        else:
                            straight_flushes.append(s)
                    elif max_pips[0] >= 4:
                        for j, count_2 in enumerate(reversed(pip_count)):
                            if count_2 >= 4:
                                four_of_a_kind_pip = 14 - j
                                return "four of a kind", self.pip(four_of_a_kind_pip) + Hand(
                                    max([card for card in self if card not in self.pip(four_of_a_kind_pip)]))
                            raise Exception("no four of a kind exists but there is a four of a kind...")
                    elif self.full_house():
                        return "full house", self.full_house()
                    flushes.append(self.suit(i).sorted()[:5])
            if straight_flushes:
                return "straight flush", max(straight_flushes)
            else:
                return "flush", max(flushes)

        if max_pips[0] >= 4:
            for i, count in enumerate(reversed(pip_count)):
                if count > 3:
                    four_of_a_kind_pip = 14 - i
                    return "four of a kind", self.pip(four_of_a_kind_pip) + Hand(
                        max([card for card in self if card not in self.pip(four_of_a_kind_pip)]))
                raise Exception("no four of a kind exists but there is a four of a kind...")

        if (max_pips[0] >= 3) & (max_pips[1] >= 2):
            if self.full_house():
                return "full house", self.full_house()

        if self.straight():
            return "straight", self.straight()

        if max_pips[0] >= 3:
            for i, count in enumerate(reversed(pip_count)):
                if count >= 3:
                    three_of_a_kind_pip = 14 - i
                    return "three of a kind", self.pip(three_of_a_kind_pip) + Hand(
                        *[card for card in self if card not in self.pip(three_of_a_kind_pip)]
                    ).sorted()[:2]
            raise Exception("no three of a kind exists but there is a three of a kind...")
        if max_pips[0] >= 2:
            if max_pips[1] >= 2:
                return "two pair", self.two_pair()
            else:
                for i, count in enumerate(reversed(pip_count)):
                    if count >= 2:
                        pair_pip = 14 - i
                        return "pair", self.pip(pair_pip) + Hand(
                            *[card for card in self if card not in self.pip(pair_pip)]).sorted()[:3]
                raise Exception("no pair exists but there is a pair...")
        return "high card", self.sorted()[:5]

    def compare(self, other):
        """
        Compares two poker hands.

        Returns 1 if self > other, 0 if self == other, -1 if self < other
        :param other: Hand; the other poker hand
        :return: int; a value indicating the outcome of the comparison
        """
        self_val = self.val()
        other_val = other.val()

        if poker_ranks[self_val[0]] != poker_ranks[other_val[0]]:
            return -1 if poker_ranks[self_val[0]] < poker_ranks[other_val[0]] else 1
        else:
            for self_card, other_card in zip(self_val[1], other_val[1]):
                if self_card.pip != other_card.pip:
                    return -1 if self_card.pip < other_card.pip else 1
        return 0

    def __eq__(self, other):
        return True if self.compare(other) == 0 else False

    def __lt__(self, other):
        return True if self.compare(other) == -1 else False

    def __le__(self, other):
        return True if self.compare(other) < 1 else False


class Player:
    def __init__(self, name, chips=None, sitting=True):
        self.Hand = Hand()
        self.name = str(name)
        self.chips = chips
        self.sitting = sitting
        self.fold = False
        self.id = random.randint(0, 2**16)  # for the hash function so that a dictionary of players can be made

    def __hash__(self):
        """
        This is just so players can be put in a dictionary and bets can be more easily tracked in the table class
        """
        return hash((self.name, self.id, self.__class__.__name__))

    def __eq__(self, other):
        return self is other

    def get(self, other):
        if isinstance(other, Cards.Card):
            self.Hand.append(other)
        if isinstance(other, Cards.Hand):
            self.Hand = self.Hand + other

    def push(self, msg, bet):
        # action = fold, check, call, bet, raise, allin
        amt = 0
        action = input(msg['action']).replace(' ', '').lower()
        if (action == 'bet') or (action == 'raise'):
            while amt < bet:
                user_input = input(msg['bet']).replace(' ', '').lower()
                try:
                    amt = int(user_input)
                    amt = amt if amt <= self.chips else 0  # make sure you don't bet more than the chips you have
                except TypeError:
                    if user_input == 'allin':
                        action = 'allin'
                        break
                    else:
                        print(f'\nTypeError - please enter a number greater than {bet} or type "all in"')

        if action == 'fold':
            self.fold = True
            amt = 0
        elif (action == 'check') and (bet != 0):
            amt = 0
        elif action == 'call':
            amt = bet
        elif (action == 'bet') or (action.lower() == 'raise'):
            pass
        elif action == 'allin':
            action = 'raise' if self.chips > bet else 'allin'
            amt = self.chips
        else:
            action, amt = self.push(msg, bet)

        if amt >= self.chips:
            amt = self.chips
            action = 'allin'
        elif amt < 0:
            amt = 0
            action = 'fold'

        self.chips += -amt
        return action, amt

    def delete(self):
        self.Hand = Hand()

    def stand(self):
        self.sitting = False

    def sit(self):
        self.sitting = True

    def reset(self):
        self.Hand = Hand()


class Table:
    def __init__(self, *Players):
        self.Players = list(Players)
        self.states = {player: 'init' for player in Players}
        self.pot = {}  # empty dict to keep track of bets
        self.dealer = 0  # keep track of who is dealing
        self.deck = Cards.Deck(cards=None, decks=1, shuffled=True)
        self.state = 'begin'
        self.community = Hand()

    def __repr__(self):
        return str(self.Players)

    def __str__(self):
        return str(self.Players)

    def players_ordered(self):
        return self.Players[self.dealer:] + self.Players[:self.dealer]

    def __iter__(self):
        """
        next will return (current player, current bet)
        """
        return Round(self, self.players_ordered(), self.states)

    def reset(self):
        self.states = {player: 'init' for player in self.Players}
        self.pot = {}
        self.dealer = (self.dealer + 1) % len(self.Players)
        self.deck = Cards.Deck(cards=None, decks=1, shuffled=True)
        self.state = 'begin'
        self.community = Hand()

    def betting_round(self):
        bets = {player: 0 for player in self.Players}
        for player in self:
            message = f"Current bet: {max(bets.values())}\nInput action:"
            action, amt = player.push(message, max(bets.values()))
            bets[player] += amt
            self.bet_state_update(player, action)
        for player in bets:
            self.pot[player] += bets[player]

    def bet_state_update(self, bettor, action):
        if action in ('bet', 'raise'):
            for player in self.states:
                if self.states[player] not in ('fold', 'allin'):
                    if player != bettor:
                        self.states[player] = 'init'
        self.states[bettor] = action

    def deal(self, cards=2, burn=False):
        if self.state == 'begin':
            self.deck.deal(*self.Players, 5, burn=True)
            self.betting_round()
            self.state = 'deal'
        else:
            raise TableError('the table must be in "deal" state to proceed to flop')

    def flop(self):
        if self.state == 'deal':
            self.deck.deal(self.community, 3, burn=True)
            self.betting_round()
            self.state = 'flop'
        else:
            raise TableError('the table must be in "deal" state to proceed to flop')

    def turn(self):
        if self.state == 'flop':
            self.deck.deal(self.community, 1, burn=True)
            self.betting_round()
            self.state = 'turn'
        else:
            raise TableError('the table must be in "flop" state to proceed to turn')

    def river(self):
        if self.state == 'turn':
            self.deck.deal(self.community, 1, burn=True)
            self.betting_round()
            self.state = 'river'
        else:
            raise TableError('the table must be in "turn" state to proceed to river')

    def resolve(self):
        winners = []

        # TODO: TEST THIS
        if len(self.playing) == 1:
            winners = [self.playing[0]]
        else:
            for i, player in enumerate(self.playing):
                winners = [player]
                for other in self.playing[i+1:]:
                    if player.Hand + self.community == other.Hand + self.community:
                        winners.append(other)
                    elif player.Hand + self.community < other.Hand + self.community:
                        winners = []
                        break
                if len(winners) > 0:
                    break  # break if winners contains the best hands

        for winner in winners:
            winner.chips += int(self.pot/len(winners))

        self.pot = 0
        self.reset()


class Round:
    """
    A Round class handles each betting round in a poker game.

    players must be passed in as a list such that they are in order from left of the dealer
    """
    def __init__(self, table: Table, players: list, states: dict):
        self.n = 0
        self.table = table
        self.players = players
        self.states = states  # incl. init, fold, check, call, bet, raise, allin

    def __iter__(self):
        return self

    def state_eval(self):
        """Return True if betting cycle is complete"""
        return all([(state not in ('init', 'fold', 'allin')) for state in self.states.values()])

    def __next__(self):
        """Returns the current player and the current bet, breaks if betting has completed"""
        if self.state_eval():
            raise StopIteration()

        current_player = self.players[self.n]

        while self.state[self.players[self.n]] != 'init':
            self.n = (self.n + 1) % len(self.players)

        return current_player, self.current_bet()


class Deck:
    def push(self, player):
        if isinstance(player, Player):
            player.get(self[0])
            del self[0]

    def deal(self, Players, cards, burn=False):
        if cards * len(Players) > len(self):
            raise IndexError(f"dealing would require {int(cards * len(Players)) + burn}, however there are only "
                             f"{len(self)} cards left in this deck")
        else:
            if burn:
                del self[0]
            for card in range(cards):
                for player in Players:
                    self.push(player)
