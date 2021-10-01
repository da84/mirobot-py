import time

from mirobot import Mirobot
from time import sleep
import socket


class MirobotServer:
    def __init__(self, ip="192.168.178.143", port=5005, buffer_size=1024):
        print("Server ist starting...", end="")
        self.__address = ip
        self.__port = port
        self.__buffer_size = buffer_size
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.__address, self.__port))
        self.__socket.listen(1)
        self._callbacks_move = []
        self._callbacks_home = []
        self._callbacks_zero = []
        self._callbacks_connect = []
        self._callbacks_disconnect = []
        position1 = [-86, 184.4, 230.3]
        position2 = [17.7, 202.6, 230.6]
        position3 = [143.8, 148.3, 230.6]
        machine1 = [-17.9, -205.5, 28.3]
        machine2 = [103.4, -178.4, 28.3]
        loading_station = [206.2, 0.3, 28.3]
        self.__positions = [position1, position2, position3]
        self.__machines = [loading_station, machine1, machine2]
        self.robot = Mirobot(wait=True, debug=False)
        print(" finished (Address = ", self.__address, ":", self.__port, ")", sep="")
        self.robot.home_simultaneous()
        #self.run()

    def __onConnect(self, ip):
        print("Client connected with IP:", ip)
        for callback in self._callbacks_connect:
            callback()

    def __onDisconnect(self):
        for callback in self._callbacks_disconnect:
            callback()

    def __onHome(self):
        self.robot.home_simultaneous()
        for callback in self._callbacks_disconnect:
            callback()

    def __onZero(self):
        self.robot.go_to_zero()
        for callback in self._callbacks_zero:
            callback()

    def __onMove(self, src, dst):
        self.__move2Position(src)
        print("An der Quelle angekommen")
        # greife
        time.sleep(2)
        self.robot.go_to_zero()
        self.__move2Position(dst)
        # lasse los
        time.sleep(2)
        print("Am Ziel angekommen")
        self.robot.go_to_zero()
        for callback in self._callbacks_move:
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
                self.__onMove(int(splitted[1]), int(splitted[2]))
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

    def __move2Position(self, position):
        if position < 1:
            position = abs(position) % 3
            pos = self.__machines[position]
        else:
            position = (position - 1) % 3
            pos = self.__positions[position]
        self.robot.go_to_cartesian_ptp(pos[0], pos[1], pos[2])