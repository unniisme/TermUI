from .TUIElement import TUIElement
from .TUIEvents import TUIInputEvent
import curses

class TUIWindowElement(TUIElement):

    def __init__(self, x, y, width, height, drawBorder = False):
        self.window : curses.window = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.drawBorder = drawBorder

    def Init(self):
        self.window = curses.newwin(self.height, self.width, self.y, self.x)

    def GetRender(self) -> dict[tuple, tuple]:
        """
        Returns a set of points in the format
        { (x,y) : (character, curses color pair) }
        """
        return {}
    
    def Render(self):
        if self.drawBorder: self.window.border()
        pts = self.GetRender()
        for pt in pts:
            x, y = pt
            self.window.addch(y, x, *pts[pt])

    def main(self, dt):
        """
        Called every dt interval
        """
        pass

    def Rerender(self):
        """
        Call when ui is updated
        """
        pass

    def InputEventHandler(self, event : TUIInputEvent):
        """
        Override to handler input
        """
        pass