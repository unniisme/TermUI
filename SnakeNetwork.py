import curses
from Snake import Direction, Snake, SnakeGame
from SnakeMain import SnakeGameTUI
from TermUI.TUI import ColorPairs, logger
from TermUI.TUIEvents import TUIInputEvent
from TermUI.TUINetworkElements import ClientElement, ServerElement
import pickle

RED = ColorPairs.AddPair(curses.COLOR_RED)
BLUE = ColorPairs.AddPair(curses.COLOR_BLUE)
GREEN = ColorPairs.AddPair(curses.COLOR_GREEN)
YELLOW = ColorPairs.AddPair(curses.COLOR_YELLOW)
MAGENTA = ColorPairs.AddPair(curses.COLOR_MAGENTA)
SNAKECOLORS = [RED, BLUE, GREEN, YELLOW, MAGENTA]

class GameState:

    def __init__(self, game : SnakeGame):
        self.max = game.max
        self.fruit = game.fruit
        self.snakes = [
            {
                "name" : snake,
                "body" : pickle.dumps(game.snakes[snake].body, 0),
                "color" : game.snakes[snake].color
            } for snake in game.snakes
        ]
    
    def Serialize(game : SnakeGame) -> str:
        return pickle.dumps(GameState(game), 0).decode()

    def Deserialize(game : SnakeGame, msg : str):
        ser : GameState = pickle.loads(msg.encode())
        game.max = ser.max
        game.fruit = ser.fruit
        game.snakes = {}
        for snake in ser.snakes:
            game.snakes[snake["name"]] = Snake(snake["name"], None, None, None)
            game.snakes[snake["name"]].body = pickle.loads(snake["body"])
            game.snakes[snake["name"]].color = snake["color"]


class InputState:
    # Look I was feeling funky when I wrote this class okay
    # It works trust me

    KEY_TO_STR = {
            curses.KEY_RIGHT : "RIGHT",
            curses.KEY_LEFT : "LEFT",
            curses.KEY_UP : "UP",
            curses.KEY_DOWN : "DOWN",
        }

    STR_TO_DIR = {
            "RIGHT" : Direction.RIGHT,
            "LEFT" : Direction.LEFT,
            "UP" : Direction.UP,
            "DOWN" : Direction.DOWN,
            "" : None
    }

    def __init__(self, input):
        self.value = ""
        if input in InputState.KEY_TO_STR:
            self.value = InputState.KEY_TO_STR[input]
            

    def GetDirection(s):
        return InputState.STR_TO_DIR[s]
    
    def __str__(self):
        return self.value



class SnakeServerTUI(SnakeGameTUI):

    def __init__(self, x, y, width, height, server : ServerElement, drawBorder=False, fruitColor=1):
        super().__init__(x, y, width, height, drawBorder, fruitColor)

        self.serverUI = server

    def Init(self):
        super().Init()

        self.serverUI.server.newSessionEvent += self.NewSnakeSession

    def main(self, dt):
        super().main(dt)

        self.serverUI.server.SendToAllSessions(GameState.Serialize(self.game))

    def NewSnakeSession(self, sID):
        self.game.NewSnake(str(sID))
        self.game.snakes[str(sID)].color = SNAKECOLORS[len(self.serverUI.server.sessions) - 1]
        self.serverUI.server.sessions[sID].recieveEvent += lambda msg : self.SnakeController(sID, msg)

    def SnakeController(self, sID, msg):
        d = InputState.GetDirection(msg)
        if d:
            self.game.Turn(str(sID), d)
        


class SnakeClientTUI(SnakeGameTUI):

    def __init__(self, x, y, width, height, client : ClientElement, drawBorder=False, fruitColor=1):
        super().__init__(x, y, width, height, drawBorder, fruitColor)

        self.clientUI = client

    def Init(self):
        super().Init()
        self.clientUI.client.messageRecieveEvent += self.HandleRecieve

    def HandleRecieve(self, msg):
        if not msg: return
        try:
            GameState.Deserialize(self.game, msg)
        except Exception as e:
            logger.error(e)
            logger.debug(msg)
        self.Rerender()

    def InputEventHandler(self, event: TUIInputEvent):
        s = InputState(event.key)
        if s:
            self.clientUI.client.EnqueData(str(s))

    def main(self, dt):
        pass # updated by server requests