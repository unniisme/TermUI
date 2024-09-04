from Snake import Snake, SnakeGame, Direction
from TermUI.TUI import TUI, ColorPairs, logger
from TermUI.TUIElements import TUIWindowElement, TextElement
from TermUI.TUIEvents import TUIInputEvent
import curses


RED = ColorPairs.AddPair(curses.COLOR_RED)
BLUE = ColorPairs.AddPair(curses.COLOR_BLUE)

x_mult = 2

class SnakeGameTUI(TUIWindowElement):

    def __init__(self, x, y, width, height, drawBorder = False, fruitColor = 1):
        super().__init__(x, y, width, height, drawBorder)

        self.game : SnakeGame = None
        self.fruitColor = fruitColor

    def Init(self):
        super().Init()
        max_y, max_x = self.window.getmaxyx()
        self.game = SnakeGame(max_x//x_mult, max_y)

    def main(self, dt):
        if self.game:
            self.game.Update(dt)
            self.Rerender()

    def GamePosToTUIPos(self, p):
        x, y = p
        return (x*x_mult, y)

    def GetRender(self) -> dict[tuple, tuple]:
        pts = {}
        for snake in self.game.snakes.values():
            pts = pts | {
                self.GamePosToTUIPos(p.position) : (str(p), curses.color_pair(snake.color))
                    for p in snake.body
            }

        if self.game.fruit:
            return pts | {
                (self.GamePosToTUIPos(self.game.fruit)) : (SnakeGame.FRUIT, curses.color_pair(self.fruitColor))
            }
        else:
            return pts

class ScoreText(TextElement):

    def __init__(self, game : SnakeGameTUI, name : str, x, y, width, height, drawBorder = False, color=1):
        super().__init__(x, y, width, height, drawBorder, text="0",
                         horizontalAlignment=TextElement.Alignment.LEFT)
        self.score = 0
        self.name = name
        self.game : SnakeGameTUI = game
        self.snake : Snake = None
        self.color = color
        self.keyMapping = {
            curses.KEY_RIGHT : Direction.RIGHT,
            curses.KEY_LEFT : Direction.LEFT,
            curses.KEY_UP : Direction.UP,
            curses.KEY_DOWN : Direction.DOWN,
        }
    
    def SetKeyMapping(self, left, right, up, down):
        self.keyMapping = {
            right : Direction.RIGHT,
            left : Direction.LEFT,
            up : Direction.UP,
            down : Direction.DOWN,
        }
    
    def Increment(self, amount = 1, cutoff = 0):
        self.score += amount
        if self.score < cutoff:
            self.score = cutoff
        self.Text(str(self.score))

    def Init(self):
        super().Init()
        self.attr = curses.color_pair(self.color)
        self.snake = self.game.game.NewSnake(self.name)
        self.snake.FruitEatEvent += self.Increment 
        self.game.game.TailEatEvent += self.HandleTailCutEvent
        self.snake.color = self.color

    def InputEventHandler(self, event):
        ch = event.key
        if ch in self.keyMapping:
            self.snake.Turn(self.keyMapping[ch])

    def HandleTailCutEvent(self, eater, eaten, amount):
        if eater == self.snake:
            if eaten == self.snake:
                self.Increment(-amount)


if __name__ == "__main__":
    tui = TUI()
    game = SnakeGameTUI(2, 2, 40, 20, drawBorder = True)
    scoreboard_1 = ScoreText(game, "1", 42, 2, 20, 3, color=RED)
    scoreboard_2 = ScoreText(game, "2", 42, 5, 20, 3, color=BLUE)
    scoreboard_2.SetKeyMapping(ord('a'),
                               ord('d'),
                               ord('w'),
                               ord('s'))

    tui.AddElement(game)
    tui.AddElement(scoreboard_1)
    tui.AddElement(scoreboard_2)

    curses.wrapper(tui.main)
    