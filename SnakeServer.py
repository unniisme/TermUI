import curses
from SnakeNetwork import SnakeServerTUI
from TermUI.TUI import TUI
from TermUI.TUINetworkElements import ServerElement

tui = TUI()

server = ServerElement(0, 0, 10, 1, ipv6=True)
server.show = False

game = SnakeServerTUI(2, 2, 40, 20, server, drawBorder=True)

tui.AddElement(server)
tui.AddElement(game)

curses.wrapper(tui.main)