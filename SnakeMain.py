from Snake import SnakeGame, Direction
from TermUI.TUI import TUI, logger
from TermUI.TUIElements import TUIWindowElement
from TermUI.TUIEvents import TUIInputEvent
import curses

x_mult = 2

class SnakeGameTUI(TUIWindowElement):

    def __init__(self, *args, stepTime=0.07, **kwargs):
        super().__init__(*args, **kwargs)

        self.game : SnakeGame = None
        self.time = 0
        self.stepTime = stepTime
        self.doubleSpeed = False

    def Init(self):
        super().Init()
        max_y, max_x = self.window.getmaxyx()
        self.game = SnakeGame(max_x//x_mult, max_y)

    
    def main(self, dt):
        self.time += dt
    
        if ((self.time >= self.stepTime)
            or (self.time >= self.stepTime/3 and self.doubleSpeed)):
            self.game.Update()
            self.Rerender()
            self.time = 0

    def InputEventHandler(self, event : TUIInputEvent):
        cases = {
                curses.KEY_RIGHT : Direction.RIGHT,
                curses.KEY_LEFT : Direction.LEFT,
                curses.KEY_UP : Direction.UP,
                curses.KEY_DOWN : Direction.DOWN,
            }
        if event.key in cases:
            self.game.Turn(cases[event.key])
            self.doubleSpeed = self.game.snake[0].direction == cases[event.key]

    def GamePosToTUIPos(self, p):
        x, y = p
        return (x*x_mult, y)

    def GetRender(self) -> dict[tuple, tuple]:
        snake = {
            (self.GamePosToTUIPos(p.position)) : (str(p),)
                for p in self.game.snake
        }

        if self.game.fruit:
            return snake | {
                (self.GamePosToTUIPos(self.game.fruit)) : (SnakeGame.FRUIT)
            }
        else:
            return snake
        
    

if __name__ == "__main__":
    tui = TUI()
    game = SnakeGameTUI(0, 0, 30, 30, drawBorder = True)

    tui.AddElement(game)
    tui.SubscibeToKeypress(game.InputEventHandler)

    curses.wrapper(tui.main)
    