class TUIScreen:
    def __init__(self, 
                 x, 
                 y,
                 max_x,
                 max_y,
                dt):
        self.x = x
        self.y = y
        self.max_x = max_x
        self.max_y = max_y
        self.dt = dt


class TUIElement:

    def __init__(self):
        self.window = None # for use by handler
        pass

    def Init(self, scr : TUIScreen):
        pass

    def GetRender(self) -> dict[tuple, tuple]:
        """
        Returns a set of points in the format
        { (y,x) : (character, curses color pair) }
        """
        return {}

    def main(self, scr : TUIScreen):
        """
        Called every few seconds
        """
        pass

    def Rerender(self):
        """
        Call when ui is updated
        """
        pass