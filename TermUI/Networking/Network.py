import socket
import threading
from queue import Queue, Empty

DEFAULT_PORT_SERVER = 8800
DEFAULT_PORT_CLIENT = 6600

class Server:

    def __init__(self, host = "0.0.0.0", port=DEFAULT_PORT_SERVER):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    def __init__(self, host, port=DEFAULT_PORT_SERVER, recieve_port=DEFAULT_PORT_CLIENT):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', recieve_port))
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
            data, _ = self.client_socket.recvfrom(1024)
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
                msg = self.queue.get(block=False)
            except Empty:
                continue
            self._SendPacket(msg)
        self.Exit(force=True)

    def Exit(self, force = False):
        """
        Call to gracefully shut down client
        """
        self.recieving = False
        self.running = False
        if not force:
            self.queue.join()

        self.client_socket.close()
        self.recieverThread.join()


