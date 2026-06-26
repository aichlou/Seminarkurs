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
        if sensorcounter == 0 and pin == 0 and state:
            timedata[sensorcounter] = time.time()
            commands.put(("stop_motor", "X"))
            speed = -speed
            sensorcounter += 1
        if sensorcounter == 1 and pin == 1 and state:
            timedata[sensorcounter] = time.time()
            commands.put(("stop_motor", "X"))
            speed = -speed
            sensorcounter += 1
    print("X-Achse der initialisierung abgeschlossen")
    speed = 0.4
    while sensorcounter < 4:
        commands.put(("start_motor", "Y", speed))
        cmd = sensordata.get()
        pin, state = cmd
        print(f"Pin {pin} ist jetzt {state}")
        if sensorcounter == 2 and pin == 2 and state:
            timedata[sensorcounter] = time.time()
            commands.put(("stop_motor", "Y"))
            speed = -speed
            sensorcounter += 1
        if sensorcounter == 3 and pin == 3 and state:
            timedata[sensorcounter] = time.time()
            commands.put(("stop_motor", "Y"))
            speed = -speed
            sensorcounter += 1
        

    duration = timedata[1] - timedata[0]
    
    unit = duration / 5
    
    commands.put(("start_motor", "X", speed))
    time.sleep(unit)
    commands.put(("stop_motor", "X"))
