import random
from TermUI.EventBus import EventBus

vector = tuple[int, int]

class Direction:

    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)

class SnakePiece:

    def __init__(self, position : vector, direction : Direction, isHead : bool = False):
        self.position = position
        self.direction = direction
        self.isHead = isHead
        

    def __str__(self):
        if self.isHead:
            return {
                Direction.RIGHT : "▶",
                Direction.LEFT : "◀",
                Direction.UP : "▲",
                Direction.DOWN : "▼"
            } [self.direction]
        else:
            return "O"
        
class Snake:

    def __init__(self, name : str, position : vector, direction : Direction, game):
        self.name = name
        
        self.body : list[SnakePiece] = [SnakePiece(position, direction, True)]
        self.inputDirection = None

        self.FruitEatEvent = EventBus()

        self.game = game

        self.timeElapsed = 0

        self.color = None # to be used externally

    def Update(self, dt : float):
        self.timeElapsed += dt

        stepTime = self.game.stepTime


        head = self.body[0]

        x, y = head.position
        dx, dy = head.direction
        newDirection = head.direction

        if self.inputDirection:
            if newDirection == self.inputDirection:
                stepTime = stepTime/3
            if sum(map(lambda t: abs(t[0] + t[1]), zip(self.inputDirection, head.direction))):
                dx, dy = self.inputDirection
                newDirection = self.inputDirection

        
        if self.timeElapsed < stepTime:
            return
        self.timeElapsed = 0
        self.inputDirection = None

        x_new, y_new = self.game.Wrap((x + dx, y + dy))

        newHead = SnakePiece((x_new, y_new), newDirection, True)
        head.isHead = False

        self.body = [newHead] + self.body

        if self.game.fruit:
            if (x_new, y_new) == self.game.fruit:
                self.game.fruit = None # Not the rigfht way to do this
                self.FruitEatEvent()
                return

        self.body.pop()

    def Turn(self, direction : Direction):
        self.inputDirection = direction

    def __str__(self):
        return "".join([str(p) for p in self.body])


class SnakeGame:

    FRUIT = "◍"

    def __init__(self, x_max : int, y_max : int, stepTime : float = 0.1):
        self.max = (x_max, y_max)

        self.fruit = None

        self.stepTime = stepTime

        self.snakes : dict[str, Snake] = {}

        self.TailEatEvent = EventBus()

    def GetFreeSpot(self):
        for x in range(self.max[0]):
            for y in range(self.max[1]):
                if self.fruit == (x,y):
                    continue
                for snake in self.snakes.values():
                    for piece in snake.body:
                        if piece.position == (x,y):
                            continue
                return (x,y)

    def NewSnake(self, name : str) -> Snake:
        snake = Snake(name, self.GetFreeSpot(), Direction.RIGHT, self)
        self.snakes[name] = snake
        return snake

    def Turn(self, name : str, direction : Direction):
        self.snakes[name].Turn(direction)
        
    def Update(self, dt : float):
        for snake in self.snakes.values():
            snake.Update(dt)
        self.UpdateFruit()
        self.HandleTailCut()

    def HandleTailCut(self):
        bodies = []
        for snake in self.snakes.values():
            for i, piece in enumerate(snake.body[1:]):
                bodies.append((i + 1, piece, snake))
        
        for snake in self.snakes.values():
            head = snake.body[0]

            for i, piece, targetSnake in bodies:
                if head.position == piece.position:
                    l = len(targetSnake.body)
                    targetSnake.body = targetSnake.body[:i]
                    self.TailEatEvent(snake, targetSnake, l-i)

    

    def Wrap(self, pos : vector) -> vector:
        x, y = pos
        x_max, y_max = self.max

        return (x%x_max, y%y_max)


    def UpdateFruit(self):
        if not self.fruit:
            self.fruit = (random.randint(0, self.max[0] - 1), random.randint(0, self.max[1]-1))

