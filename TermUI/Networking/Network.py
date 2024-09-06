import socket
import threading
from queue import Queue, Empty

DEFAULT_PORT_SERVER = 8800
DEFAULT_PORT_CLIENT = 6600

class Server:

    def __init__(self, host = None, port=DEFAULT_PORT_SERVER, ipv6 = False):
        self.port = port
        socketFamily = socket.AF_INET
        if ipv6:
            socketFamily = socket.AF_INET6
            if not host:
                host = "::"
        if not host: host = "0.0.0.0"
            

        self.host = host
        self.server_socket = socket.socket(socketFamily, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))

        self.running = False
        self.socketLock = threading.Lock()

        # TODO: timeout

    def DecodePacket(self, data : bytes):
        # Override
        return data.decode()
    
    def HandlePacket(self, data, clientAddr):
        # Override
        print(clientAddr, ":", self.DecodePacket(data))

    def main(self):
        self.running = True

        try:
            while self.running:
                self.RecievePacket()
        except:
            self.Exit()

    def RecievePacket(self):
        """
        Function to recieve a packet
        """
        with self.socketLock:
            data, clientAddr = self.server_socket.recvfrom(1024)
        while not data:
            with self.socketLock:
                data, clientAddr = self.server_socket.recvfrom(1024)
        self.HandlePacket(data, clientAddr)

    def Exit(self):
        """
        Gracefully shut down server.
        """
        self.running = False
        self.server_socket.close()
    


class Client:
    def __init__(self, host, port=DEFAULT_PORT_SERVER, recieve_port=DEFAULT_PORT_CLIENT, ipv6 = False):
        self.host = host
        self.port = port

        clientHost = "0.0.0.0"
        socketFamily = socket.AF_INET
        if ipv6:
            clientHost = "::"
            socketFamily = socket.AF_INET6

        self.client_socket = socket.socket(socketFamily, socket.SOCK_DGRAM)
        self.client_socket.bind((clientHost, recieve_port))
        self.client_socket.connect((host, port))

        self.sendLock = threading.Lock()
        self.queue = Queue()

        self.recieverThread : threading.Thread = None
        self.recieveLock = threading.Lock()
        self.running = False
        self.recieving = False

        # TODO: timeout

    def EnqueuePacket(self, message : str):
        if self.recieving:
            self.queue.put(self.EncodePacket(message))

    def _SendPacket(self, message):
        with self.sendLock:
            self.client_socket.sendall(message)

    def EncodePacket(self, data : str):
        # Override
        return data.encode()

    def HandlePacket(self, data : bytes):
        # Override
        print(data)

    def RecievePacket(self):
        with self.recieveLock:
            data, _ = self.client_socket.recvfrom(65535)
        if data:
            self.HandlePacket(data)
    
    def RecieverThreadMain(self):
        while self.recieving:
            self.RecievePacket()


    def main(self):
        self.running = True
        self.recieving = True

        self.recieverThread = threading.Thread(target = self.RecieverThreadMain)
        self.recieverThread.daemon= True
        self.recieverThread.start()

        while self.running:
            try:
                msg = self.queue.get(block=True)
            except Empty:
                continue
            self._SendPacket(msg)
        self.Exit()

    def Exit(self, force = False):
        """
        Call to gracefully shut down client
        """
        self.recieving = False
        self.running = False
        if not force:
            while not self.queue.empty():
                msg = self.queue.get()
                self._SendPacket(msg)

        self.client_socket.close()
        self.recieverThread.join()


