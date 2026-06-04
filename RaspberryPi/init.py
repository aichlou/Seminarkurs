import motor
import time
import sensor

def init(sensordata):
    print("Debug")
    motor.setup_motors()
    motor.rotate("X", 0.7)
    start = time.time()
    print("Starte x-Achsen Motor")
    commands = Queue()
    sensor = threading.Thread(target=sensor.read_sensors, args=(commands, ))
    sensor.start()
