import motor
import time
import sensor

def init(sensordata, commands):
    motor.setup_motors()
    timedata = [0.0, 0.0]
    print("Starte x-Achsen Motor")
    sensorcounter = 0
    speed = 0.7
    while not sensordata.empty():
        sensordata.get()
    while sensorcounter < 2:
        commands.put(("start_motor", "X", speed))
        cmd = sensordata.get()
        pin, state = cmd
        print(f"Pin {pin} ist jetzt {state}")
        if pin in (0, 1) and state:
            timedata[sensorcounter] = time.time()
            commands.put(("stop_motor", "X"))
            speed = -speed
            sensorcounter += 1

    duration = timedata[1] - timedata[0]
    
    unit = duration / 5
    
    commands.put(("start_motor", "X", speed))
    time.sleep(unit)
    commands.put(("stop_motor", "X"))
