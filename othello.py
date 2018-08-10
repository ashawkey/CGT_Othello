from game import *

def n2xy(n, size):
    return [n%size, n//size]

def xy2n(x, y, size):
    return int(size * y + x)


class game_Othello(game):
    '''
    The game of othello.
    Change the Col and Row to get different variants of this game.
    Note size larger than 4*4 is very hard for personal computer to solve.
    '''
    Col = 4
    Row = 4
    size = Row * Col

    def __init__(self):
        super(game_Othello, self).__init__()
        self.name = "Othello"+str(self.Col)+str(self.Row)
        self.rules = "To move: Place a chip with your color facing up on any empty square on the board such that there exists a straight " \
                     "\n(horizontal, vertical, and diagonal) line connecting that square to another square that is occupied by your piece " \
                     "\nwith all the squares in that line occupied by the opponent's pieces. There must be at least one opponent's piece " \
                     "\nin between the piece you just placed and the one it forms a straight line with." \
                     "\nAll of the opponent's pieces in that line are flipped over to your color. " \
                     "\nIf a player has no legal moves, the turn passes to the opposing player. If neither player can make a legal move, then check for the win condition.\nTo win: A game ends when neither player can make a legal move (e.g. when the board is full). " \
                     "\nAt this point, count the number of pieces each player has on the board. Whoever has a higher score wins."
        self.current = self.position(range(0, self.size), 1)

    class move():
        '''
        Legal moves for a position.
        '''
        def __init__(self, m):
            self.m = m

        def __eq__(self, other):
            return self.m == other.m if other is not None else False

        def __str__(self):
            return str(n2xy(self.m, game_Othello.Col))

    class position():
        '''
        Any possible condition/state for the game.
        '''
        def __init__(self, comp, next=1):
            self.comp = comp
            self.next = next

        def __repr__(self):
            return "".join([str(i) for i in self.comp]) + str(self.next)

        def __str__(self):
            res = ''
            for i in range(game_Othello.Row):
                for j in range(game_Othello.Col):
                    if self.comp[i * game_Othello.Col + j] == 1:
                        res += '* '
                    elif self.comp[i * game_Othello.Col + j] == 2:
                        res += '# '
                    else:
                        res += '- '
                res += '\n'
            res += "next player: " + str(self.next)
            res += "\nzero counts: " + str(self.comp.count(0))
            return res

        def __sub__(self, pos2):
            for i in range(game_Othello.size):
                if self.comp[i] != 0 and pos2.comp[i] == 0:
                    return game_Othello.move(i)

        def __eq__(self, pos2):
            return self.comp == pos2.comp and self.next == pos2.next

        def __hash__(self):
            return hash(tuple(self.comp))

    def doMove(self, p, move):
        if move is None:
            return self.position(comp=p.comp, next=3 - p.next)
        comp = list(p.comp)
        comp[move.m] = p.next
        x, y = n2xy(move.m, self.Col)
        lines = [[], [], [], []]
        for i in range(len(comp)):
            xi, yi = n2xy(i, self.Col)
            if xi == x: lines[0].append(i)
            if yi == y: lines[1].append(i)
            if xi + yi == x + y: lines[2].append(i)
            if xi - yi == x - y: lines[3].append(i)
        flag = 0
        for line in lines:
            center = 0
            mark = []
            for i in range(len(line)):
                if line[i] == move.m:
                    center = i
            mark.clear()
            for i in range(center + 1, len(line)):
                if comp[line[i]] == 3 - p.next:
                    if i == len(line) - 1:
                        mark.clear()
                    else:
                        mark.append(line[i])
                elif comp[line[i]] == p.next:
                    break
                elif comp[line[i]] == 0:
                    mark.clear()
                    break
            if mark != []:
                flag = 1
                for m in mark: comp[m] = p.next
            mark.clear()
            for i in range(center - 1, -1, -1):
                if comp[line[i]] == 3 - p.next:
                    if i == 0:
                        mark.clear()
                    else:
                        mark.append(line[i])
                elif comp[line[i]] == p.next:
                    break
                elif comp[line[i]] == 0:
                    mark.clear()
                    break
            if mark != []:
                flag = 1
                for m in mark: comp[m] = p.next
        if flag == 1:
            return self.position(comp, 3 - p.next)

    def genMove(self, p):
        comp = p.comp
        res = [self.move(index) for index, value in enumerate(comp) if value == 0 if
               self.doMove(p, self.move(index)) is not None]
        return res if res != [] else [None, ]

    def isPrimitive(self, p):
        '''
        Test whether a position is a primitive position.
        When both players have no place to go, the game ends.
        '''
        return self.genMove(p) == [None, ] and self.genMove(self.doMove(p, self.genMove(p)[0])) == [None, ]

    def primitive(self, p):
        n1 = p.comp.count(1)
        n2 = p.comp.count(2)
        if n1 > n2:
            if p.next == 1:
                return solution('win', 0, p)
            else:
                return solution('lose', 0, p)
        elif n1 == n2:
            return solution('tie', 0, p)
        else:
            if p.next == 1:
                return solution('lose', 0, p)
            else:
                return solution('win', 0, p)

    def initPosition(self):
        comp = range(0, self.size)
        comp = [0 for i in comp]
        comp[xy2n(self.Col // 2 - 1, self.Row // 2 - 1, self.Col)] = 1
        comp[xy2n(self.Col // 2, self.Row // 2 - 1, self.Col)] = 2
        comp[xy2n(self.Col // 2 - 1, self.Row // 2, self.Col)] = 2
        comp[xy2n(self.Col // 2, self.Row // 2, self.Col)] = 1
        self.current = self.position(comp, 1)
        return self.current

    def comment(self):
        print("==========")
        print(str(self.current))
        print("==========")



