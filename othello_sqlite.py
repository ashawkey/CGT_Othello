import queue
from tkinter import *
from tkinter import ttk
import os
import collections
from sqlitedict import SqliteDict


class game():
    def __init__(self):
        self.name = "Name"
        self.rules = "Rules"
        self.current = None

    def introduce(self):
        print("\n--------------------")
        print(self.name)
        print(self.rules)
        print("--------------------")

    def initPosition(self): return 0

    def isPrimitive(self, p): return 0

    def initGame(self): self.current = self.initPosition()

    def finished(self): return self.isPrimitive(self.current)


def n2xy(n, size):
    y = n // size
    x = n % size
    return [x, y]


def xy2n(x, y, size):
    return int(size * y + x)


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


class game_Othello(game):
    Col = 5
    Row = 4
    size = Row * Col

    def __init__(self):
        super(game_Othello, self).__init__()
        self.name = "Othello54"
        self.rules = "To move: Place a chip with your color facing up on any empty square on the board such that there exists a straight " \
                     "\n(horizontal, vertical, and diagonal) line connecting that square to another square that is occupied by your piece " \
                     "\nwith all the squares in that line occupied by the opponent's pieces. There must be at least one opponent's piece " \
                     "\nin between the piece you just placed and the one it forms a straight line with." \
                     "\nAll of the opponent's pieces in that line are flipped over to your color. " \
                     "\nIf a player has no legal moves, the turn passes to the opposing player. If neither player can make a legal move, then check for the win condition.\nTo win: A game ends when neither player can make a legal move (e.g. when the board is full). " \
                     "\nAt this point, count the number of pieces each player has on the board. Whoever has a higher score wins."
        self.current = self.position(range(0, self.size), 1)

    class move():
        def __init__(self, m):
            self.m = m

        def __eq__(self, other):
            return self.m == other.m if other is not None else False

        def __str__(self):
            return str(n2xy(self.m, game_Othello.Col))

    class position():
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


class solution():
    def __init__(self, state="undecided", remoteness=-1, pos=None, move=None):
        self.state = state
        self.remoteness = remoteness
        self.pos = pos
        self.move = move
        self.parents = []
        self.children = []
        self.childNum = 0

    def simplify(self):
        return solution(self.state, self.remoteness, None, self.move)

    def __str__(self):
        return self.state + " | remoteness:" + str(self.remoteness) + " | move:" + str(self.move)


class solver():
    def __init__(self, game):
        self.game = game
        self.dbName = self.game.name + "_dbS.sql"

    def solve_in_mem(self):
        database = {}
        self.solveAll(database)
        sqldb = SqliteDict(self.dbName, autocommit=True)
        for k, v in database.items():
            sqldb[k] = v.simplify()
        sqldb.close()
        print("[Solver] Graph saved to disk")

    def solve_in_disk(self):
        database = SqliteDict(self.dbName, autocommit=True)
        self.solveAll(database)
        database.close()

    def solveAll(self, database):
        print("[Solver] solve all called")
        # position to solution
        # bfs of the tree
        database.clear()
        root = self.game.initPosition()
        database[repr(root)] = solution(pos=root)
        que = queue.Queue()
        frontier = queue.Queue()
        que.put(root)
        visited = set()
        while not que.empty():
            pos = que.get()
            childPositions = [self.game.doMove(pos, m) for m in self.game.genMove(pos)]
            for child in childPositions:
                if child is not None:
                    if self.game.isPrimitive(child) and child not in visited:
                        visited.add(child)
                        sol = self.game.primitive(child)
                        database[repr(child)] = sol
                        frontier.put(child)
                    elif repr(child) not in database:
                        database[repr(child)] = solution(pos=child)
                    sol = database[repr(child)]
                    sol.parents.append(pos)
                    database[repr(child)] = sol
                    sol = database[repr(pos)]
                    sol.childNum += 1
                    sol.children.append(child)
                    database[repr(pos)] = sol
                    # database[child].parents.append(pos)
                    # database[pos].children.append(child)
                    # database[pos].childNum += 1
                    if not child in visited:
                        visited.add(child)
                        que.put(child)

        print("[Solver] Graph generated")
        # bottom up
        while not frontier.empty():
            pos = frontier.get()
            sol = database[repr(pos)]
            for parent in sol.parents:
                parSol = database[repr(parent)]
                if sol.state == 'lose':
                    if parSol.state == 'win':
                        if parSol.remoteness == -1 or parSol.remoteness > sol.remoteness + 1:
                            parSol.remoteness = sol.remoteness + 1
                            parSol.move = sol.pos - parSol.pos
                    else:
                        parSol.state = 'win'
                        parSol.remoteness = sol.remoteness + 1
                        parSol.move = sol.pos - parSol.pos
                        frontier.put(parent)
                elif sol.state == 'tie':
                    if parSol.state == 'undecided' or parSol.state == 'seen_tie':
                        if parSol.remoteness == -1 or parSol.remoteness < sol.remoteness + 1:
                            parSol.remoteness = sol.remoteness + 1
                            parSol.move = sol.pos - parSol.pos
                        parSol.childNum -= 1
                        if parSol.childNum == 0:
                            parSol.state = 'tie'
                            frontier.put(parent)
                        else:
                            parSol.state = 'seen_tie'
                elif sol.state == 'win':
                    if parSol.state == 'undecided' or parSol.state == 'seen_tie':
                        if parSol.state == 'undecided':
                            if parSol.remoteness == -1 or parSol.remoteness < sol.remoteness + 1:
                                parSol.remoteness = sol.remoteness + 1
                                parSol.move = sol.pos - parSol.pos
                        parSol.childNum -= 1
                        if parSol.childNum == 0:
                            if parSol.state == 'seen_tie':
                                parSol.state = 'tie'
                            else:
                                parSol.state = 'lose'
                            frontier.put(parent)
                database[repr(parent)] = parSol
        print("[Solver] Graph searched")
        # label draw condition
        for pos, sol in database.items():
            # choose draw rather than tie
            if sol.state == 'undecided' or sol.state == 'seen_tie':
                sol.state = 'draw'

    def printDatabase(self, database):
        for p, n in database.items():
            print("======\n" + str(p) + "\n------\n" + str(n) + "\n======")


class player():
    def __init__(self, game):
        self.game = game
        self.solver = solver(self.game)
        self.database = None
        self.database = None
        self.player1 = None
        self.player2 = None
        self.name1 = None
        self.name2 = None

    def getPrompt(self, choices, text):
        prompt = input(text)
        choices = [str(i) for i in choices]
        while not prompt in choices:
            prompt = input("Please choose from " + ', '.join(choices) + ":")
        return prompt

    def human_play(self, player):
        self.game.comment()
        sol = self.database[repr(self.game.current)]
        print("Player %s should %s in %d turn[s]" % (player, sol.state, sol.remoteness))
        transform = {str(i): i for i in self.game.genMove(sol.pos)}
        if len(transform) == 1:
            smove = list(transform.keys())[0]
            print("Player %s has only one choice: %s" % (player, smove))
        else:
            smove = self.getPrompt(transform.keys(), "Player %s's turn:" % player)
        move = transform[smove]
        self.game.current = self.game.doMove(self.game.current, move)
        print("")

    def computer_play(self, name):
        self.game.comment()
        sol = self.database[repr(self.game.current)]
        print("%s will %s in %d turn[s]" % (name, sol.state, sol.remoteness))
        print("%s chooses %s" % (name, str(sol.move)))
        self.game.current = self.game.doMove(self.game.current, sol.move)
        print("")

    def report(self, playerA, playerB):
        sol = self.game.primitive(self.game.current)
        if sol.state == 'win':
            print("%s WINs!" % playerA)
        elif sol.state == 'tie':
            print("TIE!")
        elif sol.state == 'draw':
            print("DRAW!")
        elif sol.state == 'lose':
            print("%s WINs!" % playerB)
        print("")

    def play_it(self, A, B, p1="computer", p2="computer"):
        while not self.game.finished():
            A(p1)
            if self.game.finished():
                self.report(p2, p1)
                break
            B(p2)
            if self.game.finished():
                self.report(p1, p2)

    def play(self):
        while True:
            self.game.introduce()
            print("    a) Human vs. Human")
            print("    b) Human vs. Computer")
            print("    c) Computer vs. Human")
            print("    d) Computer vs. Computer")
            print("    e) Exit")
            prompt = self.getPrompt(['a', 'b', 'c', 'd', 'e'], "Please choose from above:")
            if (prompt == 'e'):
                print("Bye!")
                break
            self.game.initGame()
            if (prompt == 'a'):
                A = input("Please input the first player's name:")
                B = input("Please input the second player's name:")
                self.play_it(self.human_play, self.human_play, A, B)
            elif (prompt == 'b'):
                H = input("Please input the human player's name:")
                self.play_it(self.human_play, self.computer_play, H)
            elif (prompt == 'c'):
                H = input("Please input the human player's name:")
                self.play_it(self.computer_play, self.human_play, "computer", H)
            elif (prompt == 'd'):
                self.play_it(self.computer_play, self.computer_play, "computer1", "computer2")
            prompt = self.getPrompt(['y', 'n', ''], "Another game? ([y]/n)")
            if prompt == 'n':
                print("Bye!")
                break
            else:
                print("")

    def analyze(self, database):
        stat = collections.OrderedDict([['win', 0], ['lose', 0], ['tie', 0], ['draw', 0]])
        total = 0
        for p, n in database.iteritems():
            stat[n.state] += 1
            total += 1
        for k, v in stat.items():
            print(k, ': ', v, ' (', 100 * v / total, '%)')
        print("Initial position's state is", database[repr(self.game.initPosition())].state)

    def connect(self):
        self.database = SqliteDict(self.solver.dbName, autocommit=True)

    def load(self):
        if os.path.isfile(self.solver.dbName):
            print("[Init] loading previously saved database:", self.solver.dbName)
            self.database = SqliteDict(self.solver.dbName, autocommit=True)
        else:
            print("[ERROR] there are no previously saved database")

    def init(self):
        def help():
            print("    S) solve in memory (slightly fast)")
            print("    s) solve in disk (slow)")
            print("    P) print (human-readable results)")
            print("    l) load")
            print("    p) play")
            print("    a) analyze (slow)")
            print("    e) exit")
            print("    h) help")

        print("-----Game Initiator-----")
        help()
        while True:
            prompt = self.getPrompt(['', 'S', 's', 'l', 'P', 'p', 'a', 'e', 'h'], ">>>")
            if prompt == 's':
                print("[Init] start solving the game in disk...")
                self.solver.solve_in_disk()
                self.connect()
            elif prompt == 'S':
                print("[Init] start solving the game in memory...")
                self.solver.solve_in_mem()
                self.connect()
            elif prompt == 'e':
                print("-------------------------")
                break
            elif prompt == '':
                pass
            elif prompt == 'h':
                help()
            elif prompt == 'l':
                self.load()
            else:
                if self.database == None:
                    print("[ERROR] please solve the game first!")
                elif prompt == 'P':
                    file = self.game.name + "_database.txt"
                    with open(file, "w") as f:
                        for p, n in self.database.items():
                            f.write("=====\n" + str(p) + "\n-----\n" + str(n) + "\n=====")
                    print("[Init] save human-readable database to " + file)
                elif prompt == 'p':
                    self.play()
                elif prompt == 'a':
                    self.analyze(self.database)

    def inquire_box(self):
        master = Tk()

        master.wm_title("Othello")

        l1 = ttk.Label(master, text="First Player: ").grid(row=0, column=0, sticky=W)

        comvalue = StringVar()
        comboxlist = ttk.Combobox(master, textvariable=comvalue)
        comboxlist.grid(row=0, column=1, sticky=N + E + W)
        comboxlist["values"] = ("Computer", "Human")
        comboxlist.current(0)

        l2 = ttk.Label(master, text="Second Player: ").grid(row=1, column=0, sticky=W)

        comvalue2 = StringVar()
        comboxlist2 = ttk.Combobox(master, textvariable=comvalue2)
        comboxlist2.grid(row=1, column=1, sticky=N + E + W)
        comboxlist2["values"] = ("Computer", "Human")
        comboxlist2.current(0)

        ttk.Label(master, text="Name 1: ").grid(row=2, column=0, sticky=W)
        name1_text = StringVar()
        entry1 = Entry(master, textvariable=name1_text)
        entry1.grid(row=2, column=1, sticky=N + E + W)
        name1_text.set("A")
        ttk.Label(master, text="Name 2: ").grid(row=3, column=0, sticky=W)
        name1_text = StringVar()
        entry2 = Entry(master, textvariable=name1_text)
        entry2.grid(row=3, column=1, sticky=N + E + W)
        name1_text.set("B")

        def clickSM():
            ttk.Label(master, text="[Init] start solving the game in memory... ").grid(sticky=W,
                                                                                       columnspan=2)
            self.solver.solve_in_mem()
            self.database = SqliteDict(self.solver.dbName, autocommit=True)
            ttk.Label(master, text="Finished. ").grid(sticky=W, columnspan=2)

        def clickP():
            if self.database == None:
                style = ttk.Style()
                style.configure("BW.TLabel", foreground="red")
                ttk.Label(master, text="[ERROR] please solve the game first! ", style="BW.TLabel").grid(
                    sticky=W,
                    columnspan=2)
            else:
                self.player1 = comboxlist.get()
                self.player2 = comboxlist2.get()
                self.name1 = entry1.get()
                self.name2 = entry2.get()
                print(self.player1, self.player2)
                master.destroy()

        def clickL():
            if os.path.isfile(self.solver.dbName):
                text1 = "[Init] loading previously saved database:" + self.solver.dbName
                ttk.Label(master, text=text1).grid(sticky=W, columnspan=2)
                self.database = SqliteDict(self.solver.dbName, autocommit=True)
                ttk.Label(master, text="Finished. ").grid(sticky=W, columnspan=2)
            else:
                style = ttk.Style()
                style.configure("BW.TLabel", foreground="red")
                ttk.Label(master, text="[ERROR] there are no previously saved database ",
                          style="BW.TLabel").grid(
                    sticky=W, columnspan=2)

        def clickSD():
            ttk.Label(master, text="[Init] start solving the game in disk... ").grid(sticky=W, columnspan=2)
            self.solver.solve_in_disk()
            self.database = SqliteDict(self.solver.dbName, autocommit=True)
            ttk.Label(master, text="Finished. ").grid(sticky=W, columnspan=2)

        def clickA():

            if self.database == None:
                style = ttk.Style()
                style.configure("BW.TLabel", foreground="red")
                ttk.Label(master, text="[ERROR] please solve the game first! ", style="BW.TLabel").grid(
                    sticky=W,
                    columnspan=2)
            else:
                stat = collections.OrderedDict([['win', 0], ['lose', 0], ['tie', 0], ['draw', 0]])
                total = 0
                for p, n in self.database.iteritems():
                    stat[n.state] += 1
                    total += 1
                for k, v in stat.items():
                    ttk.Label(master, text=str(k) + ': ' + str(v) + ' (' + str(100 * v / total) + '%)').grid(sticky=W,
                                                                                                             columnspan=2)
                t = "Initial position's state is " + self.database[repr(self.game.initPosition())].state
                ttk.Label(master, text=t).grid(sticky=W, columnspan=2)

        def clickR():
            ttk.Label(master, text=self.game.rules).grid(sticky=W, columnspan=2)

        button1 = ttk.Button(master, text="Solve in Memory", command=clickSM)
        button1.grid(row=4, column=1, sticky=N + E + W)

        button2 = ttk.Button(master, text="Play", command=clickP)
        button2.grid(row=4, column=0, sticky=N + E + W)

        button3 = ttk.Button(master, text="Load", command=clickL)
        button3.grid(row=5, column=0, sticky=N + E + W)

        button4 = ttk.Button(master, text="Solve in Disk", command=clickSD)
        button4.grid(row=5, column=1, sticky=N + E + W)

        button5 = ttk.Button(master, text="Analyse", command=clickA)
        button5.grid(row=6, column=0, sticky=N + E + W)

        button6 = ttk.Button(master, text="Rule", command=clickR)
        button6.grid(row=6, column=1, sticky=N + E + W)

        def closeWindow():
            os._exit(0)

        master.protocol('WM_DELETE_WINDOW', closeWindow)
        master.mainloop()
