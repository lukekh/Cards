from Cards import Card, Hand

poker_ranked = {
    "high card": 0,
    "pair": 1,
    "two pair": 2,
    "three of a kind": 3,
    "straight": 4,
    "flush": 5,
    "full house": 6,
    "four of a kind": 7,
    "straight flush": 8,
    "royal flush": 9
}


class Poker(Hand):
    def straight(self):
        """
        Finds the highest valued straight in a collection of cards
        :return: Poker; the highest straight, empty hand if no straight
        """
        for i in reversed(range(5, 15)):  # This makes sure we don't check for an impossible straight
            counter = 0
            consecutive = Poker()
            while len(consecutive) < 5:
                if self.pip(i - counter):  # Are there any cards with this pip, counting backward via counter
                    consecutive.append(self.pip(i - counter)[0])
                    counter += 1
                else:
                    break
            if len(consecutive) > 4:
                return consecutive
        return Poker()  # Empty if there is no straight

    def full_house(self):
        """
        Finds the highest valued full house in a collection of cards
        :return: Poker; the highest full house, empty hand if no straight
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
        return Poker()

    def two_pair(self):
        """
        Finds the highest valued two pair in a collection of cards
        :return: Poker; the highest two pair + kicker, empty hand if no straight
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
                        return pip_temp + other_pip_temp + Poker(
                            max([card for card in self if card not in (pip_temp + other_pip_temp)]))
        return Poker()

    def val(self):
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
                        for i, count in enumerate(reversed(pip_count)):
                            if count >= 4:
                                four_of_a_kind_pip = 14 - i
                                break
                        return "four of a kind", self.pip(four_of_a_kind_pip) + Poker(
                            max([card for card in self if card not in self.pip(four_of_a_kind_pip)]))
                    elif self.full_house():
                        return "full house", self.full_house()
                    flushes.append(self.suit(i).sorted()[:5])
            if straight_flushes:
                return max(straight_flushes)
            else:
                return max(flushes)

        if max_pips[0] >= 4:
            for i, count in enumerate(reversed(pip_count)):
                if count > 3:
                    four_of_a_kind_pip = 14 - i
                    break
            return "four of a kind", self.pip(four_of_a_kind_pip) + Poker(
                max([card for card in self if card not in self.pip(four_of_a_kind_pip)]))

        if (max_pips[0] >= 3) & (max_pips[1] >= 2):
            if self.full_house():
                return "full house", self.full_house()

        if self.straight():
            return "straight", self.straight()

        if max_pips[0] >= 3:
            for i, count in enumerate(reversed(pip_count)):
                if count >= 3:
                    three_of_a_kind_pip = 14 - i
                    break
            return "three of a kind", self.pip(three_of_a_kind_pip) + Poker(
                *[card for card in self if card not in self.pip(three_of_a_kind_pip)]
            ).sorted()[:2]

        if max_pips[0] >= 2:
            if max_pips[1] >= 2:
                return "two pair", self.two_pair()
            else:
                for i, count in enumerate(reversed(pip_count)):
                    if count >= 2:
                        pair_pip = 14 - i
                        break
                return "pair", self.pip(pair_pip) + Poker(
                    *[card for card in self if card not in self.pip(pair_pip)]).sorted()[:3]

        return "high card", self.sorted()[:5]

    def compare(self, other):
        """
        Compares two Poker hands.

        Returns 1 if self > other, 0 if self == other, -1 if self < other
        :param other: Poker; the other Poker hand
        :return: int; a value indicating the outcome of the comparison
        """
        self_val = self.val()
        other_val = other.val()

        if poker_ranked[self_val[0]] != poker_ranked[other_val[0]]:
            return -1 if poker_ranked[self_val[0]] < poker_ranked[other_val[0]] else 1
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
