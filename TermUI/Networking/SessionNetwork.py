import TermUI.Networking.Network as Network
from queue import Queue, Empty
from ..EventBus import EventBus
from .UAP import Message, UAP
import threading
import logging
import random
default_logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='TUI.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='[%(name)-8s][ %(levelname)7s ] %(message)s'
)

class Session:
    def __init__(self, clientAddr, startMainThread = True):
        self.clientAddr = clientAddr

        self.queue = Queue()
        self.running = False
        self.recieveEvent = EventBus()

        self.thread : threading.Thread = None

        if startMainThread:
            self.thread = threading.Thread(target = self.main)
            self.thread.daemon = True
            self.thread.start()


    def main(self):
        self.running = True

        while self.running:
            try:
                msg = self.queue.get(timeout=1)
            except Empty:
                continue
            self.recieveEvent(msg)

    def Exit(self):
        self.running = False
        self.thread.join()

def EncodeMessage(msg : Message) -> bytes:
    return msg.EncodeMessage()

def DecodeMessage(data : bytes) -> Message:
    return Message.DecodeMessage(data)


class SessionServer(Network.Server):
    
    def __init__(self, host = "0.0.0.0", 
                 port=Network.DEFAULT_PORT_SERVER,
                 logger=default_logger):
        super().__init__(host, port)
        self.logger = logger

        self.sessions : dict[int, Session] = {}

        self.newSessionEvent = EventBus()
        self.sessionCloseEvent = EventBus()


    def DecodePacket(self, data: bytes) -> Message:
        return DecodeMessage(data)

    def HandlePacket(self, data, clientAddr):
        msg = self.DecodePacket(data)

        self.logger.debug(msg)

        if msg.command == UAP.CommandEnum.HELLO:

            session = Session(clientAddr)
            self.sessions[msg.sID] = session
            self.server_socket.sendto(data, clientAddr)

            self.newSessionEvent(msg.sID)
            self.logger.info(f"Session created : {msg.sID} : {clientAddr}")

        elif msg.command == UAP.CommandEnum.DATA:
            if msg.sID not in self.sessions:
                self.logger.warn(f"Obtained DATA from unknown sID : {msg.sID}")
                return
            
            self.sessions[msg.sID].queue.put(msg.message)

        elif msg.command == UAP.CommandEnum.GOODBYE:
            self.sessions[msg.sID].Exit()
            self.sessionCloseEvent(msg.sID)

    def SendMessageToSession(self, sID, message : str):
        if sID not in self.sessions:
            return
        
        clientAddr = self.sessions[sID].clientAddr
        pass


class SessionClient(Network.Client):
    
    class State:
        HELLO = 0
        ALIVE = 1
        CLOSING = 2

    def __init__(self, host, 
                 port=Network.DEFAULT_PORT_SERVER, 
                 recieve_port=Network.DEFAULT_PORT_CLIENT,
                 logger=default_logger):
        super().__init__(host, port, recieve_port)
        self.logger = logger

        self.sID = random.getrandbits(32)
        self.seq = 0

        self.messageRecieveEvent = EventBus()
        self.stateChangeEvent = EventBus()
        self.SetState(SessionClient.State.HELLO)


    def Seq(self):
        self.seq += 1
        return self.seq - 1
    
    def SetState(self, state : State):
        self.state = state
        self.stateChangeEvent(state)


    def EnqueuePacket(self, message: Message):
        if self.recieving:
            self.queue.put(message.EncodeMessage())

    def EnqueData(self, message : str):
        self.EnqueuePacket(Message(
            UAP.CommandEnum.DATA,
            self.Seq(),
            self.sID,
            message
        ))

    def main(self):
        self.recieving = True
        self.EnqueuePacket(Message(
            UAP.CommandEnum.HELLO,
            self.Seq(),
            self.sID,
            ""
        ))

        super().main()

    
    def HandlePacket(self, data : bytes):
        msg = DecodeMessage(data)
        if self.state == SessionClient.State.HELLO:
            if msg.command == UAP.CommandEnum.HELLO:
                self.SetState(SessionClient.State.ALIVE)

        elif self.state == SessionClient.State.ALIVE:
            if msg.command == UAP.CommandEnum.GOODBYE:
                self.Exit()

            elif msg.command == UAP.CommandEnum.DATA:
                self.messageRecieveEvent(msg.message)

    def Exit(self, force = False):
        self.SetState(SessionClient.State.CLOSING)
        self.EnqueuePacket(Message(
            UAP.CommandEnum.GOODBYE,
            self.Seq(),
            self.sID,
            ""
        ))
        super().Exit(force)

        

    