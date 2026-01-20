import time
import threading
import webserver
import motor
from queue import Queue

def temp(index, value):
    webserver.set_state(index, value)
    print(f"State {index} auf {value} gesetzt")
    time.sleep(5)
    webserver.set_state(index, not value)
    print(f"State {index} auf {not value} gesetzt")

commands = Queue()
host = threading.Thread(target=webserver.host_server, args=(commands, ))
host.start()
print("Hosting Webserver")
commands.put(("change_state", 0, True))
while True:
    cmd = commands.get()
    command, *args = cmd
    match command:
        case "start_motor":
            rotate = threading.Thread(target=motor.rotate, args=args)
            rotate.start()
        case "change_state":
            change = threading.Thread(target=temp, args=args)
            change.start()
        case "stop_motor":
            motor.stop_motor()
        case _:
            raise Exception("This is an Error")