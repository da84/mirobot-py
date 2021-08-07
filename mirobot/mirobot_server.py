from mirobot import Mirobot
import socket


class MirobotServer:
    def __init__(self, ip="127.0.0.1", port=5005, buffer_size=1024):
        print("Server ist starting...", end="")
        self.__address = ip
        self.__port = port
        self.__buffer_size = buffer_size
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.__address, self.__port))
        self.__socket.listen(1)
        self.__callbacks_move = []
        self.__callbacks_home = []
        self.__callbacks_zero = []
        self.__callbacks_connect = []
        self.__callbacks_disconnect = []
        self.robot = Mirobot(wait=True, debug=False)
        print(" finished (Address = ", self.__address, ":", self.__port, ")", sep="")
        self.run()

    def __onConnect(self, ip):
        print("Client connected with IP:", ip)
        for callback in self.__callbacks_connect:
            callback()

    def __onDisconnect(self):
        for callback in self.__callbacks_disconnect:
            callback()

    def __onHome(self):
        self.robot.home_simultaneous()
        for callback in self.__callbacks_disconnect:
            callback()

    def __onZero(self):
        for callback in self.__callbacks_zero:
            callback()

    def __onMove(self, src, dst):
        for callback in self.__callbacks_move:
            callback(src, dst)

    def run(self):
        print("Server is listening...")
        connection, client_address = self.__socket.accept()
        self.__onConnect(client_address)
        data = self.__receive(connection)
        while data != b"CLOSE":
            if data == b"HOME":
                self.__onHome()
                self.__sendACK(connection)
            elif data == b"ZERO":
                self.__onZero()
                self.__sendACK(connection)
            elif data.startswith(b"MOVE;"):
                splitted = data.decode().split(";")
                self.__onMove(splitted[1], splitted[2])
                self.__sendACK(connection)
            else:
                self.__sendACK(connection)
            data = self.__receive(connection)
        self.__onDisconnect()

    def __receive(self, connection):
        while True:
            data = connection.recv(self.__buffer_size)
            if not data: continue
            print("Received:", data.decode())
            return data

    def __sendACK(self, connection):
        print("Sending...", end="")
        connection.send(b"ACK")
        print(" finished")