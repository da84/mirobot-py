from mirobot import MirobotServer
from time import sleep
s = MirobotServer()
while True:
    try:
        s.run()
    except Exception as exc:
        print(exc)
