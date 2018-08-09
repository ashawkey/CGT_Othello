from sqlitedict import SqliteDict
import queue

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

