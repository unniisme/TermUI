import random

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

class SnakeGame:

    FRUIT = "◍"

    def __init__(self, x_max : int, y_max : int, stepTime : float = 0.07):
        self.max = (x_max, y_max)

        head = SnakePiece((x_max//2, y_max//2), Direction.RIGHT, True)
        self.snake = [head]
            # [ head, b1, b2, b3 ..... ]

        self.fruit = None

        self.inputDirection = None

        self.stepTime = stepTime
        self.timeElapsed = 0


    def Turn(self, direction : Direction):
        self.inputDirection = direction
        
    def Update(self, dt : float):
        self.UpdateSnake(dt)
        self.UpdateFruit()
        self.HandleTailCut()

    def HandleTailCut(self):
        head = self.snake[0]

        for i in range(len(self.snake) - 1):
            if head.position == self.snake[i+1].position:
                self.snake = self.snake[:i]
                return

    def Wrap(self, pos : vector) -> vector:
        x, y = pos
        x_max, y_max = self.max

        return (x%x_max, y%y_max)

    def UpdateSnake(self, dt : float):
        self.timeElapsed += dt

        stepTime = self.stepTime


        head = self.snake[0]

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

        x_new, y_new = self.Wrap((x + dx, y + dy))

        newHead = SnakePiece((x_new, y_new), newDirection, True)
        head.isHead = False

        self.snake = [newHead] + self.snake

        if self.fruit:
            if (x_new, y_new) == self.fruit:
                self.fruit = None

            else:
                self.snake.pop()


    def UpdateFruit(self):
        if not self.fruit:
            self.fruit = (random.randint(0, self.max[0] - 1), random.randint(0, self.max[1]-1))

