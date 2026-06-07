import motor
import time
import sensor

def init(sensordata, commands):
    motor.setup_motors()
    commands.put(("start_motor", "X", 0.7))
    start = time.time()
    print("Starte x-Achsen Motor")
    while not sensordata.empty():
        sensordata.get()
    while True:
        cmd = sensordata.get()
        pin, state = cmd
        print(f"Pin {pin} ist jetzt {state}")
        if pin in (0, 1) and state:
            commands.put(("stop_motor", "X"))
            time.sleep(3)
            commands.put(("start_motor", "X", -0.7))
            print("Stoppe Motor")
            
