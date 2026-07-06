import time
from queue import Empty
import motor

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


def _wait_for_sensor(sensordata, index, timeout=50):
    start_time = time.time()
    while True:
        try:
            pin, state = sensordata.get(timeout=0.5)
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
    commands.put(("start_motor", "X", 0.25))
    time.sleep(unit)
    commands.put(("stop_motor", "X"))
