import curses
import threading
import logging
import time

from .TUIEvents import TUIInputEvent, TUIInputEventReactor
from .TUIElements import TUIWindowElement

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='TUI.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='[%(name)-8s][ %(levelname)7s ] %(message)s'
)


class ColorPairs:

    PAIRS = [
        (1, curses.COLOR_WHITE, curses.COLOR_BLACK),
    ]
    i = 1
    isInvert = False

    def AddPair(fg, bg) -> int:
        ColorPairs.i += 1
        ColorPairs.PAIRS.append((ColorPairs.i, fg, bg))
        return ColorPairs.i

    def Init():
        if ColorPairs.isInvert:
            for pair in ColorPairs.PAIRS:
                curses.init_pair(pair[0], pair[2], pair[1])
        else:
            for pair in ColorPairs.PAIRS:
                curses.init_pair(*pair)

    def Invert():
        ColorPairs.isInvert = not ColorPairs.isInvert
        ColorPairs.Init()

class TUI:

    DTIME = 0.001

    def __init__(self):
        self.pressedKey = None
        self.writeLock = threading.Lock()
        self.readLock = threading.Lock()
        self.takingInput = True
        self.keyEventBus = []
        self.SubscibeToKeypress(TUIInputEventReactor(self.DefaultKeyHandler))

        self.cursor_x = 0
        self.cursor_y = 0
        self.Elements : list[TUIWindowElement] = []
        self.shouldRender = True
        self.rendering = True

        self.stdscr : curses.window = None
        self.running = True

    # -------- Keypress handling ----------------
    def SubscibeToKeypress(self, reactor : TUIInputEventReactor):
        """
        Reactor is a single argument function
        with the parameter as the key
        """
        self.keyEventBus.append(reactor)

    def KeyPressMain(self):
        logger.info("Key press thread started")
        try:
            while self.takingInput:
                with self.writeLock:
                    ch = self.stdscr.getch()
                if ch == -1:
                    continue
                logger.debug(f"Input {ch}")

                inputEvent = TUIInputEvent(ch)

                for reactor in self.keyEventBus:
                    try:
                        reactor(inputEvent)
                    except Exception as e:
                        # Log
                        logger.warn(
                            "Reactor error on reactor " +
                            str(reactor) +
                            " and input " +
                            str(ch) +
                            f"\nError: {e}"
                        )
        except Exception as e:
            import traceback
            logger.error(f"Key press handler crashed with error {e}")
            logger.debug(traceback.format_tb(e.__traceback__))

            self.running = False


    def DefaultKeyHandler(self, event : TUIInputEvent):
        if event.key == 4:
            logger.info("EOL")
            self.running = False
        if event.key == ord("i"):
            ColorPairs.Invert()  
            self.Rerender()


    # --------------------------------------------

    # ------------ Rendering ---------------------

    def RenderMain(self):

        logger.info("Render thread started")
        try:
            while self.rendering:
                if not self.shouldRender:
                    time.sleep(TUI.DTIME)
                    continue

                for element in self.Elements:
                    with self.writeLock:
                        element.window.erase()
                        element.Render()
                        element.window.refresh()
                
                with self.writeLock:
                    self.stdscr.move(self.cursor_y, self.cursor_x)
                    self.stdscr.refresh()

                self.shouldRender = False
                time.sleep(TUI.DTIME)



        except Exception as e:
            import traceback
            logger.error(f"Renderer crashed with error {e}")
            logger.debug("".join(traceback.format_tb(e.__traceback__)))

            self.running = False

    def Rerender(self):
        self.shouldRender = True

    # --------------------------------------------

    def AddElement(self, element: TUIWindowElement):
        self.Elements.append(element)
        element.Rerender = self.Rerender

        self.SubscibeToKeypress(element.InputEventHandler)

    def Init(self):

        ColorPairs.Init()

        # Set up input mode
        curses.curs_set(1)
        curses.raw()         # Disable line buffering
        curses.noecho()      # Do not display input characters
        self.stdscr.nodelay(1)    # Non blocking input
        self.stdscr.keypad(True)  # Enable special keys (e.g., arrow keys)

        # Init each element
        for element in self.Elements:
            element.Init()

        # Start thread for handling input
        self.keyThread = threading.Thread(target=self.KeyPressMain)
        self.keyThread.daemon = True
        self.keyThread.start()

        # Start thread for handling rendering
        self.renderThread = threading.Thread(target=self.RenderMain)
        self.renderThread.daemon = True
        self.renderThread.start()


    def main(self, stdscr : curses.window):
        self.stdscr = stdscr

        self.Init()

        try:
            while self.running:
                for element in self.Elements:
                    element.main(TUI.DTIME)
                time.sleep(TUI.DTIME)
        except Exception as e:
            logging.error(f"Main thread crashed with error {e}")
            raise e
