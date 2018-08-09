from cmdPlayer import *
import time
from threading import Thread


class cell:
    '''
    Othello board cell
    '''
    size = 80
    edge = 3
    hint_size = 5
    first = ['#333333', '#555555']
    second = ['#faebd7', '#fffafa']
    fill = '#ffd700'
    color = '#d2691e'
    edge_color = "#8b4513"
    piece_edge = 3

    def __init__(self, tk, cv, x, y):
        self.x, self.y = x, y
        self.state = 0
        self.sol = None
        self.hint = True
        self.cv = cv
        self.tk = tk
        self.outer = cv.create_rectangle(x - self.size / 2, y - self.size / 2, x + self.size / 2, y + self.size / 2,
                                         fill=self.color, outline=self.edge_color, width=5)
        self.inner = cv.create_rectangle(x - self.size / 2 + self.edge, y - self.size / 2 + self.edge,
                                         x + self.size / 2 - self.edge, y + self.size / 2 - self.edge, fill=self.fill,
                                         outline='')
        self.piece = cv.create_oval(x - self.size / 2 + 2 * self.edge, y - self.size / 2 + 2 * self.edge,
                                    x + self.size / 2 - 2 * self.edge, y + self.size / 2 - 2 * self.edge,
                                    fill=self.fill, outline=self.fill, width=self.piece_edge)
        self.hintPiece = cv.create_oval(x - self.hint_size, y - self.hint_size, x + self.hint_size, y + self.hint_size,
                                        fill=self.fill, outline=self.fill, activewidth=5)

    def flip(self, fro, to, wait=True):
        if wait:
            tmp = fro
            for t in range(int(-self.size / 2 + 2 * self.edge), int(self.size / 2 - 2 * self.edge), 2):
                self.cv.delete(self.piece)
                self.piece = self.cv.create_oval(self.x - self.size / 2 + 2 * self.edge,
                                                 self.y + t,
                                                 self.x + self.size / 2 - 2 * self.edge,
                                                 self.y - t,
                                                 fill=tmp[0], outline=tmp[1], width=self.piece_edge
                                                 )
                self.tk.update()
                time.sleep(0.0001)
                if t == 0: tmp = to
        else:
            self.cv.itemconfig(self.piece, fill=to[0], outline=to[1])

    def update_state(self, state):
        wait = True
        if self.state != state:
            if self.state == 0: wait = False
            if state == 1:
                self.cv.itemconfig(self.hintPiece, fill=self.fill, outline=self.fill)
                self.flip(self.second, self.first, wait)
                self.cv.itemconfig(self.hintPiece, fill=self.first, outline=self.first)
            elif state == 2:
                self.cv.itemconfig(self.hintPiece, fill=self.fill, outline=self.fill)
                self.flip(self.first, self.second, wait)
                self.cv.itemconfig(self.hintPiece, fill=self.second, outline=self.second)
            elif state == 0:
                self.cv.itemconfig(self.piece, fill=self.fill, outline=self.fill)
            self.state = state

    def hint_colorRamp(self, sol, hint):
        if not hint:
            return 'blue'
        if sol is None:
            return self.fill
        if sol.state == 'win':
            return 'red'
        elif sol.state == 'lose':
            return 'green'
        elif sol.state == 'tie' or sol.state == 'draw':
            return 'yellow'

    def update_hint(self, sol, hint=True):
        self.sol, self.hint = sol, hint
        if self.state == 0:
            factor = 1
            if sol is not None and hint:
                if sol.state == 'win':
                    factor = 1 + 2 * (sol.remoteness / game_Othello.size)
                elif sol.state == 'lose':
                    factor = 2 - 0.5 * (sol.remoteness / game_Othello.size)
            self.cv.delete(self.hintPiece)
            self.hintPiece = self.cv.create_oval(self.x - self.hint_size * factor, self.y - self.hint_size * factor,
                                                 self.x + self.hint_size * factor, self.y + self.hint_size * factor,
                                                 fill=self.hint_colorRamp(sol, hint),
                                                 outline=self.hint_colorRamp(sol, hint),
                                                 activewidth=5)


class gui_player():
    '''
    GUI specially for Othello
    '''
    def __init__(self, game=game_Othello()):
        self.game = game
        self.player = player(game)
        self.player.inquire_box()
        self.width, self.height = 800, 600
        self.tk = Tk(className='Player')
        self.tk.geometry('+%d+%d' % (int(self.tk.winfo_screenwidth() - self.width) // 2, 10))
        self.tk.resizable(0, 0)
        self.cv = Canvas(width=self.width, height=self.height, highlightthickness=0, background="#adff2f")
        self.cv.pack()
        self.x, self.y = 0, 0
        self.board = []
        self.pos = self.game.initPosition()
        self.history = [self.pos, ]
        self.current = 0
        self.hint = False
        self.lock = False
        self.wait = True
        self.who = None
        self.Who = None
        self.comment = None

    def bind_callback(self):
        def mouse_action(event):
            if self.lock: return
            self.x = event.x
            self.y = event.y
            [j, i] = self.pxl2xy(self.x, self.y)
            move = self.game.move(xy2n(i, j, self.game.Col))
            legalMoves = self.game.genMove(self.pos)
            if legalMoves == [None, ]:
                self.pos = self.game.doMove(self.pos, None)
                self.update_by_position()
                self.wait = False
            elif move in legalMoves:
                if move is not None:
                    self.pos = self.game.doMove(self.pos, move)
                    self.update_by_position(move)
                    self.wait = False

        def undo(event):
            if self.lock: return
            if self.current >= 2:
                self.current -= 2
                self.pos = self.history[self.current]
                self.update_by_position()
                self.update_by_position()
            else:
                print("most earlier")

        def redo(event):
            if self.lock: return
            if self.current <= len(self.history) - 2:
                self.current += 2
                self.pos = self.history[self.current]
                self.update_by_position()
                self.update_by_position()
            else:
                print("most late")

        def hint(event):
            self.hint = False if self.hint == True else True
            self.update_by_position()
            self.update_by_position()

        def new(event):
            if self.lock: return
            self.tk.destroy()
            self.player.inquire_box()
            self.width, self.height = 800, 600
            self.tk = Tk(className='Player')
            self.tk.geometry('+%d+%d' % (int(self.tk.winfo_screenwidth() - self.width) // 2, 10))
            self.tk.resizable(0, 0)
            self.cv = Canvas(width=self.width, height=self.height, highlightthickness=0, background="#adff2f")
            self.cv.pack()
            self.x, self.y = 0, 0
            self.board = []
            self.pos = self.game.initPosition()
            self.history = [self.pos, ]
            self.current = 0
            self.hint = False
            self.lock = False
            self.wait = True
            self.who = None
            self.Who = None
            self.comment = None
            self.init()
            self.new = False

        self.tk.bind("<Button-1>", mouse_action)
        self.cv.tag_bind(self.undoButton, "<Button-1>", undo)
        self.cv.tag_bind(self.redoButton, "<Button-1>", redo)
        self.cv.tag_bind(self.resetButton, "<Button-1>", new)
        self.cv.tag_bind(self.hintButton, "<Button-1>", hint)

    def decorate(self):
        main_color = '#ff3871'
        if 'Decoration':
            deco_pos, deco_size = 0, 200
            self.cv.create_polygon(
                (deco_pos, 0), (deco_pos + deco_size, 0),
                (deco_pos, deco_size),
                outline='',
                fill=main_color)
            x, y = 0, deco_size
            for i in range(5):
                self.cv.create_polygon((x, y), (x + deco_size / 4, y), (x, y + deco_size / 4), fill=main_color)
                x += deco_size / 4
                y -= deco_size / 4

    def update_by_position(self, firstMove=None):
        self.lock = True
        legalMoves = self.game.genMove(self.pos)
        change = list(enumerate(self.pos.comp))
        if firstMove is not None:
            first = (firstMove.m, self.pos.comp[firstMove.m])
            change.remove(first)
            change.insert(0, first)
        for i, s in change:
            x, y = n2xy(i, self.game.Col)
            move = self.game.move(i)
            if move in legalMoves:
                npos = self.game.doMove(self.pos, move)
                sol = self.player.database[repr(npos)]
                self.board[y][x].update_hint(sol, self.hint)
            else:
                self.board[y][x].update_hint(None)
            self.board[y][x].update_state(s)

        if self.current + 1 > len(self.history) - 2 or len(self.history) < 2:
            self.cv.itemconfig(self.redoButton, state=DISABLED)
        else:
            self.cv.itemconfig(self.redoButton, state=NORMAL)

        if self.current + 1 < 2:
            self.cv.itemconfig(self.undoButton, state=DISABLED)
        else:
            self.cv.itemconfig(self.undoButton, state=NORMAL)

        if self.game.finished():
            self.cv.itemconfig(self.resetButton, state=NORMAL)
        else:
            self.cv.itemconfig(self.resetButton, state=DISABLED)

        self.lock = False

    def pxl2xy(self, x, y):
        for i in range(self.game.Row):
            for j in range(self.game.Col):
                b = self.board[i][j]
                if x > b.x - b.size / 2 and x < b.x + b.size / 2 and y > b.y - b.size / 2 and y < b.y + b.size / 2:
                    return [i, j]
        return [-1, -1]

    def run_screen(self):
        if 'board':
            board_leftUp = (self.width / 2 - cell.size * self.game.Col / 2 + cell.size / 2,
                            self.height / 2 - cell.size * self.game.Row / 2 + cell.size / 2)
            for i in range(self.game.Row):
                self.board.append([])
                for j in range(self.game.Col):
                    self.board[i].append(
                        cell(self.tk, self.cv, board_leftUp[0] + j * cell.size, board_leftUp[1] + i * cell.size))

        if 'button':
            hint_x = 4 * self.width / 8
            undo_x = 5 * self.width / 8
            redo_x = 6 * self.width / 8
            reset_x = 7 * self.width / 8
            button_y = 1 * self.height / 10
            button_font = ('Courier', -25, 'bold')
            self.undoButton = self.cv.create_text(undo_x, button_y, text="Undo", font=button_font,
                                                  activefill='blue', disabledfill='grey', tag=('button'))
            self.redoButton = self.cv.create_text(redo_x, button_y, text="Redo", font=button_font,
                                                  activefill='blue', disabledfill='grey', tag=('button'))
            self.resetButton = self.cv.create_text(reset_x, button_y, text="Reset", font=button_font,
                                                   activefill='blue', disabledfill='grey', tag=('button'))
            self.hintButton = self.cv.create_text(hint_x, button_y, text="Hint", font=button_font,
                                                  activefill='blue', disabledfill='grey', tag=('button'))

        self.bind_callback()
        self.update_by_position()

    def init(self):
        self.pos = self.game.initPosition()
        self.run_screen()
        self.decorate()

        if self.player.player1 == 'Human' and self.player.player2 == 'Human':
            self.target = lambda: self.play_it(self.human_play, self.human_play, self.player.name1, self.player.name2)
        elif self.player.player1 == 'Human' and self.player.player2 == 'Computer':
            self.wait = True
            self.target = lambda: self.play_it(self.human_play, self.computer_play, self.player.name1)
        elif self.player.player1 == 'Computer' and self.player.player2 == 'Human':
            self.wait = False
            self.target = lambda: self.play_it(self.computer_play, self.human_play, "computer", self.player.name2)
        else:
            self.wait = False
            self.target = lambda: self.play_it(self.computer_play, self.computer_play, "computer1", "computer2")

        self._play_thread = Thread(target=self.target)
        self._play_thread.start()
        mainloop()

    def update_history(self):
        while len(self.history) > self.current + 1:
            self.history.pop()
        self.history.append(self.pos)
        self.current += 1

    def update_text(self, name, textColor, pieceColor):
        self.cv.delete(self.comment)
        self.cv.delete(self.Who)
        self.cv.delete(self.who)
        self.edge = 35
        self.Who = self.cv.create_oval(6 * self.width / 8 + 2 * self.edge + 100,
                                       2 * self.height / 8 + 2 * self.edge + 150,
                                       6 * self.width / 8 - 2 * self.edge + 100,
                                       2 * self.height / 8 - 2 * self.edge + 150,
                                       fill=pieceColor[0], outline=pieceColor[1], width=5)
        self.who = self.cv.create_text(6 * self.width / 8 + 100, 2 * self.height / 8 + 150, text=name, fill=textColor,
                                       font=("Courier", -25, 'italic'))
        sol = self.player.database[repr(self.game.current)]
        t2 = name + " will " + sol.state + " in " + str(sol.remoteness) + " turn[s]"
        if sol.move is None:
            t2 += '\nYou have no place to go, click to skip.'
        self.comment = self.cv.create_text(self.width / 2, 7 * self.height / 8, text=t2, fill='black',
                                           font=("Courier", -25, 'bold'), justify=CENTER)

    def report(self, playerA, playerB):
        print(playerA, playerB)
        n1 = self.pos.comp.count(1)
        n2 = self.pos.comp.count(2)
        text = ''
        if n1 > n2:
            text = "%s WINs!" % playerA
        elif n1 == n2:
            text = "TIE!"
        elif n1 < n2:
            text = "%s WINs!" % playerB
        self.cv.delete(self.comment)
        self.comment = self.cv.create_text(self.width / 2, 7 * self.height / 8, text=text, fill='black',
                                           font=("Courier", -25, 'bold'), justify=CENTER)

    def play_it(self, A, B, p1="computer", p2="computer"):
        self.game.current = self.pos
        while not self.player.game.finished():
            self.update_text(p1, cell.second, cell.first)
            A(p1)
            self.game.current = self.pos
            self.update_history()
            if self.player.game.finished():
                self.new = True
                break
            self.update_text(p2, cell.first, cell.second)
            B(p2)
            self.game.current = self.pos
            self.update_history()
            if self.player.game.finished():
                self.new = True
                break
        self.report(p1, p2)
        self.update_by_position()

    def human_play(self, player):
        self.wait = True
        while self.wait:
            time.sleep(0.05)

    def computer_play(self, name):
        self.lock = True
        time.sleep(0.5)
        sol = self.player.database[repr(self.pos)]
        self.pos = self.game.doMove(self.pos, sol.move)
        self.update_by_position(sol.move)
        time.sleep(0.5)
        self.lock = False


if __name__ == '__main__':
    g = gui_player(game_Othello())
    g.init()
