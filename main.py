import time
import threading
import webserver
import motor
from queue import Queue

commands = Queue()
host = threading.Thread(target=webserver.host_server, args=(commands, ))
host.start()
print("Hosting Webserver")

motor.setup_motors()
while True:
    cmd = commands.get()
    command, *args = cmd
    match command:
        case "start_motor":
            rotate = threading.Thread(target=motor.rotate, args=args)
            rotate.start()
        case _:
            raise Exception("This is an Error")