import time
import threading
import webserver
import motor
import sensor
from queue import Queue
import init

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
motor.setup_motors()
print("Motors are set up")
sensor = threading.Thread(target=sensor.read_sensors, args=(commands, ))
sensor.start()
sensordata = Queue()
while True:
    print("Warte auf Befehle...")
    cmd = commands.get()
    command, *args = cmd
    match command:
        case "start_motor":
            print("Starting motor thread")
            rotate = threading.Thread(target=motor.rotate, args=args)
            rotate.start()
        case "change_state":
            change = threading.Thread(target=webserver.set_state, args=args)
            change.start()
            Sensordata.put(command)
        case "stop_motor":
            print("Stopping motor")
            motor.stop_motor(args[0])
        case "initialize":
            print("Initializing system")
            ini = threading.Thread(target=init.init, args=(sensordata, ))
            
        case _:
            raise Exception("This is an Error")