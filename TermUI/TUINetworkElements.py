from .Networking.SessionNetwork import SessionServer, SessionClient
from .TUIElements import TUIWindowElement
from .TUI import logger
import threading

class ServerElement(TUIWindowElement):
    """
    Both a UAP server-client endpoint and a TUI Element
    Server uses port 8800 and client 6600 by default
    """

    def __init__(self, x, y, width, height, drawBorder = False,
                 host = "0.0.0.0", server_port = 8800):
        super().__init__(x, y, width, height, drawBorder)

        self.server = SessionServer(host, server_port)
        self.serverThread = None

        self.sessionMessageBuffer = {}

        self.server.newSessionEvent += self.RegisterSession
        self.server.sessionCloseEvent += self.DeRegisterSession
        

    def RegisterSession(self, sID):
        self.sessionMessageBuffer[sID] = ""
        self.server.sessions[sID].recieveEvent += lambda msg : self.UpdateSessionBuffer(sID, msg)
        self.Rerender()

    def DeRegisterSession(self, sID):
        del self.sessionMessageBuffer[sID]
        self.Rerender()

    def UpdateSessionBuffer(self, sID, msg):
        self.sessionMessageBuffer[sID] = msg
        self.Rerender()


    def Init(self):
        super().Init()

        self.serverThread = threading.Thread(target = self.server.main)
        self.serverThread.daemon = True
        self.serverThread.start()

    def Render(self):
        if self.drawBorder: self.window.border()
        y = 1
        max_y, max_x = self.window.getmaxyx()
        max_x = max_x - 2
        for sID in self.sessionMessageBuffer:
            if y > max_y:
                return
            
            self.window.addnstr(y, 1, f"{hex(sID)} : {self.sessionMessageBuffer[sID]}", max_x)
            y += 1


class ClientElement(TUIWindowElement):

    def __init__(self, x, y, width, height, drawBorder = False,
                 host = "0.0.0.0", server_port = 8800, client_port = 6600):
        
        super().__init__( x, y, width, height, drawBorder)

        self.client = SessionClient(host, server_port, client_port)
        self.clientThread = None
        self.buffer = ""

        self.client.messageRecieveEvent += self.UpdateMessageBuffer

    def UpdateMessageBuffer(self, msg):
        self.buffer = msg
        self.Rerender()

    def Init(self):
        super().Init()

        self.clientThread = threading.Thread(target = self.client.main)
        self.clientThread.daemon = True
        self.clientThread.start()

    def Render(self):
        if self.drawBorder: self.window.border()
        _, max_x = self.window.getmaxyx()
        self.window.addnstr(0, 0, f"Connected to {self.client.host}:{self.client.port}", max_x)
        self.window.addnstr(1, 0, self.buffer, max_x)
        

