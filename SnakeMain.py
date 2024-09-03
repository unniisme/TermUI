from Snake import Snake, SnakeGame, Direction
from TermUI.TUI import TUI, logger
from TermUI.TUIElements import TUIWindowElement, TextElement
from TermUI.TUIEvents import TUIInputEvent
import curses

x_mult = 2

class SnakeGameTUI(TUIWindowElement):

    def __init__(self, x, y, width, height, drawBorder = False):
        super().__init__(x, y, width, height, drawBorder)

        self.game : SnakeGame = None
        self.defaultSnake : Snake = None

    def Init(self):
        super().Init()
        max_y, max_x = self.window.getmaxyx()
        self.game = SnakeGame(max_x//x_mult, max_y)

        self.defaultSnake = self.game.NewSnake("default")

    def main(self, dt):
        if self.game:
            self.game.Update(dt)
            self.Rerender()

    def InputEventHandler(self, event):
        ch = event.key
        cases = {
                curses.KEY_RIGHT : Direction.RIGHT,
                curses.KEY_LEFT : Direction.LEFT,
                curses.KEY_UP : Direction.UP,
                curses.KEY_DOWN : Direction.DOWN,
            }
        if ch in cases:
            self.defaultSnake.Turn(cases[ch])

    def GamePosToTUIPos(self, p):
        x, y = p
        return (x*x_mult, y)

    def GetRender(self) -> dict[tuple, tuple]:
        pts = {}
        for snake in self.game.snakes.values():
            pts = pts | {
                self.GamePosToTUIPos(p.position) : (str(p),)
                    for p in snake.body
            }

        if self.game.fruit:
            return pts | {
                (self.GamePosToTUIPos(self.game.fruit)) : (SnakeGame.FRUIT,)
            }
        else:
            return snake

class ScoreText(TextElement):

    def __init__(self, game : SnakeGameTUI, x, y, width, height, drawBorder = False):
        super().__init__(x, y, width, height, drawBorder, text="0",
                         horizontalAlignment=TextElement.Alignment.RIGHT)
        self.score = 0
        self.game = game
    
    def Increment(self):
        self.score += 1
        self.Text(str(self.score))

    def Init(self):
        super().Init()
        self.game.defaultSnake.FruitEatEvent += self.Increment 


    

if __name__ == "__main__":
    tui = TUI()
    game = SnakeGameTUI(10, 10, 40, 20, drawBorder = True)
    scoreboard = ScoreText(game, 10, 30, 40, 3)

    tui.AddElement(game)
    tui.AddElement(scoreboard)

    curses.wrapper(tui.main)
    