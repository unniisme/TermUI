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


class TextElement(TUIWindowElement):

    class Alignment:
        CENTRE = 0
        LEFT = 1
        RIGHT = 2
        TOP = -1
        BOTTOM = -2

    def __init__(self, x, y, width, height, drawBorder = False, 
                 text : str = "", wrap : bool = False,
                 horizontalAlignment : Alignment = 1, verticalAlignment : Alignment = -1):
        super().__init__(x, y, width, height, drawBorder = False)

        self.text = text
        self.wrap = wrap  # TODO
        self.horizontalAlignment = horizontalAlignment
        self.verticalAlignment = verticalAlignment

    def Text(self, t : str):
        self.text = t
        self.Rerender()

    def Render(self):
        _, width = self.window.getmaxyx()

        n = len(self.text)

        if self.horizontalAlignment == TextElement.Alignment.LEFT:
            text = self.text[:width]
        elif self.horizontalAlignment == TextElement.Alignment.RIGHT:
            text = self.text[-width:]
        elif self.horizontalAlignment == TextElement.Alignment.CENTRE:
            text = self.text[(n-width)//2, (n+width)//2]

        self.window.addnstr(text, width)