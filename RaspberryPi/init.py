import time
from queue import Empty
import motor
import state

SENSOR_SIDES = {
    "X": [0, 1],
    "Y": [2, 3],
}


def _clear_queue(queue):
    while True:
        try:
            queue.get_nowait()
        except Empty:
            break


def _wait_for_sensor(sensordata, index, timeout=500):
    start_time = time.time()
    while True:
        try:
            pin, state = sensordata.get(timeout=0.01)
        except Empty:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Sensor {index} wurde nicht rechtzeitig ausgelöst")
            continue

        if pin == index and state:
            return time.time()


def _home_axis(axis, commands, sensordata, speed=0.4): #0.7
    first_index, second_index = SENSOR_SIDES[axis]
    print(f"Initialisiere Achse {axis} - erste Position")
    commands.put(("start_motor", axis, speed))
    first_time = _wait_for_sensor(sensordata, first_index)
    commands.put(("stop_motor", axis))
    time.sleep(0.1)

    print(f"Initialisiere Achse {axis} - zweite Position")
    commands.put(("start_motor", axis, -speed))
    second_time = _wait_for_sensor(sensordata, second_index)
    commands.put(("stop_motor", axis))
    time.sleep(0.1)

    return second_time - first_time


def init(sensordata, commands):
    motor.setup_motors()
    _clear_queue(sensordata)
    timedata = [0.0, 0.0, 0.0, 0.0]
    print("Starte x-Achsen Motor")
    sensorcounter = 0
    speed = 0.6
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
    speed = 0.7
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
    try:
        duration_x = _home_axis("X", commands, sensordata, speed=0.4)
        print("X-Achse der Initialisierung abgeschlossen")
    except TimeoutError as exc:
        print("Initialisierung X-Achse fehlgeschlagen:", exc)
        return

    try:
        _home_axis("Y", commands, sensordata, speed=0.4)
        print("Y-Achse der Initialisierung abgeschlossen")
    except TimeoutError as exc:
        print("Initialisierung Y-Achse fehlgeschlagen:", exc)
        return

    unit = duration_x / 5
    print(f"Bewege X-Achse um eine Einheit: {unit:.3f} Sekunden")
    commands.put(("0"))
    time.sleep(0.01)
    
    # Signalisiere, dass Init fertig ist
    state.init_complete = True
    #commands.put(("start_motor", "X", 0.25))
    #time.sleep(unit)
    #commands.put(("stop_motor", "X"))
