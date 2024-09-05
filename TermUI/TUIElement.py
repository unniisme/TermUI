class TUIElement:

    def __init__(self):
        self.window = None # for use by handler
        self.children : list[TUIElement] = []

    def Init(self):
        for child in self.children:
            child.Init()

    def GetRender(self) -> dict[tuple, tuple]:
        """
        Returns a set of points in the format
        { (y,x) : (character, curses color pair) }
        """
        return {}

    def main(self, dt : float):
        """
        Called every few seconds
        """
        for child in self.children:
            child.main(dt)

    def Rerender(self):
        """
        Call when ui is updated
        """
        pass

    def AddChild(self, child):
        self.children.append(child)