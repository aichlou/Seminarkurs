import motor
import time
import sensor

def init(sensordata, commands):
    print("Debug")
    motor.setup_motors()
    commands.put(("start_motor", "X", 0.7))
    start = time.time()
    print("Starte x-Achsen Motor")
    while True:
        cmd = sensordata.get()
        pin, state = cmd
        print(f"Pin {pin} ist jetzt {state}")
