from SnakeNetwork import SnakeClientTUI
from TermUI.TUI import TUI
from TermUI.TUINetworkElements import ClientElement
import curses
import sys


host = "::"
port = 8800
recv_port = 6600

if '--host' in sys.argv:
    host = sys.argv[sys.argv.index('--host') + 1]
if '--port' in sys.argv:
    port = int(sys.argv[sys.argv.index('--port') + 1])
if '--recvport' in sys.argv:
    recv_port = int(sys.argv[sys.argv.index('--recvport') + 1])

tui = TUI()

client = ClientElement(0, 0, 10, 1, host=host, server_port=port, client_port=recv_port, ipv6=True)
client.show = False
game = SnakeClientTUI(2, 2, 40, 20, client, drawBorder=True)

tui.AddElement(client)
tui.AddElement(game)

curses.wrapper(tui.main)