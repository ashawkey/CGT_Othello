from solver import *

class game():
    '''
    Abstract class of all games.
    '''
    def __init__(self):
        self.name = "Name"
        self.rules = "Rules"
        self.current = None

    def introduce(self):
        print("\n--------------------")
        print(self.name)
        print(self.rules)
        print("--------------------")

    def initPosition(self): pass

    def isPrimitive(self, p): pass

    def primitive(self,p): pass

    def doMove(self, p, m): pass

    def genMove(self,p): pass

    def comment(self): pass

    def initGame(self): self.current = self.initPosition()

    def finished(self): return self.isPrimitive(self.current)


class game_oneTwoTen(game):
    def __init__(self):
        super(game_oneTwoTen, self).__init__()
        self.name = "One, Two, ..., Ten"
        self.rules = "Rules: try to reach ten first, each turn choose from 1 and 2"
        self.goal = 10
        self.current = 0

    def doMove(self, p, m):
        return p + m

    def genMove(self, p):
        if p >= self.goal:
            return []
        elif p == self.goal - 1:
            return [1, ]
        else:
            return [1, 2]

    def isPrimitive(self, p):
        return p == self.goal

    def primitive(self, p):
        if p == self.goal: return solution('lose', 0, 10, 0)

    def initPosition(self):
        return 0

    def comment(self):
        print("Current number is %d" % self.current)


class game_OddEven:
    class move():
        def __init__(self, stride=0, who="nobody"):
            self.stride = stride
            self.who = who

        def __str__(self):
            return str(self.stride)

    class position:
        def __init__(self, remain, first=0, second=0, next="first"):
            self.remain = remain
            self.next = next
            self.first = first
            self.second = second

        def __repr__(self):
            return str((self.remain, self.next, self.first, self.second))

        def __str__(self):
            return "remain:" + str(self.remain) + " first:" + str(self.first) + " second:" + str(
                self.second) + " next:" + self.next

        def __sub__(self, pos2):
            return game_OddEven.move(pos2.remain - self.remain, pos2.next)

        def __eq__(self, pos2):
            return self.remain == pos2.remain and self.first == pos2.first and self.second == pos2.second and self.next == pos2.next

        def __hash__(self):
            return hash((self.remain, self.next, self.first, self.second))

    def __init__(self):
        self.name = "OddEven!"
        self.rules = "Rules: try to get even number of matches when game ends"
        self.total = 15
        self.current = self.position(self.total)

    def doMove(self, p, m):
        if (p.next == "first"):
            nfirst = p.first + m.stride
            nsecond = p.second
            nnext = "second"
        else:
            nfirst = p.first
            nsecond = p.second + m.stride
            nnext = "first"
        return self.position(p.remain - m.stride, nfirst, nsecond, nnext)

    def genMove(self, p):
        if p.remain >= 3:
            return [self.move(i, p.next) for i in [1, 2, 3]]
        elif p.remain == 2:
            return [self.move(i, p.next) for i in [1, 2]]
        elif p.remain == 1:
            return [self.move(1, p.next), ]
        else:
            return []

    def isPrimitive(self, p):
        return p.remain == 0

    def primitive(self, p):
        if p.first % 2 == 0 and p.next == "second":
            return solution('lose', 0, p)
        elif p.first % 2 == 0 and p.next == "first":
            return solution('win', 0, p)
        elif p.second % 2 == 0 and p.next == "first":
            return solution('lose', 0, p)
        elif p.second % 2 == 0 and p.next == "second":
            return solution('win', 0, p)

    def initPosition(self):
        return self.position(self.total)

    def introduce(self):
        print(self.name)
        print(self.rules)

    def initGame(self):
        self.current = self.initPosition()

    def finished(self):
        return self.isPrimitive(self.current)

    def comment(self):
        print("Current remain is " + str(self.current.remain) + ", first player has " + str(
            self.current.first) + ", second palyer has " + str(self.current.second))

