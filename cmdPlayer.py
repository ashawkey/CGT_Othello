from othello import *
from solver import *
from tkinter import *
from tkinter import ttk
import os
import collections


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


if __name__ == '__main__':
    p = player(game_Othello())
    p.init()
