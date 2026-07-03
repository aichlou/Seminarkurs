import time
import threading
import lgpio

stop_event_x = threading.Event()
stop_event_y = threading.Event()
stop_event_z = threading.Event()
h = None

MOTOR_PINS = {
    "X": {"PUL": 14, "DIR": 15, "ENA": 18},
    "Y": {"PUL": 17, "DIR": 27, "ENA": 22},
}


def get_handle():
    global h
    if h is None:
        h = lgpio.gpiochip_open(0)
    return h


def setup_motors():
    global h
    if h is not None:
        try:
            lgpio.gpiochip_close(h)
        except Exception:
            pass
    h = lgpio.gpiochip_open(0)

    for axis, pins in MOTOR_PINS.items():
        lgpio.gpio_claim_output(h, pins["PUL"], 0)
        lgpio.gpio_claim_output(h, pins["DIR"], 0)
        lgpio.gpio_claim_output(h, pins["ENA"], 0)
        lgpio.gpio_write(h, pins["ENA"], 1)

def rotate(axis, speed):
    handle = get_handle()
    if axis not in MOTOR_PINS:
        print("Ungültiger Motorindex:", repr(axis))
        raise ValueError("Ungültiger Motorindex")

    if axis == "X":
        stop_event_x.clear()
        stop_event = stop_event_x
    elif axis == "Y":
        stop_event_y.clear()
        stop_event = stop_event_y
    else:
        stop_event_z.clear()
        stop_event = stop_event_z

    pins = MOTOR_PINS[axis]
    if speed == 0:
        lgpio.gpio_write(handle, pins["ENA"], 1)
        print(f"Motor {axis} wurde nicht gestartet: Geschwindigkeit ist 0")
        return

    direction = 1 if speed < 0 else 0
    lgpio.gpio_write(handle, pins["DIR"], direction)
    lgpio.gpio_write(handle, pins["ENA"], 0)
    speed = abs(speed)
    pause = 1 / (40 * (speed + 10))

    print(f"Starte Motor {axis} mit Geschwindigkeit {speed}, Richtung {direction}")
    try:
        while not stop_event.is_set():
            lgpio.gpio_write(handle, pins["PUL"], 1)
            time.sleep(pause)
            lgpio.gpio_write(handle, pins["PUL"], 0)
            time.sleep(pause)
    except Exception as exc:
        print("Fehler beim Drehen des Motors:", exc)
    finally:
        lgpio.gpio_write(handle, pins["ENA"], 1)
        lgpio.gpio_write(handle, pins["DIR"], 0)
        print("Motor gestoppt")


def stop_motor(axis):
    if axis == "X":
        stop_event_x.set()
    elif axis == "Y":
        stop_event_y.set()
    else:
        print("Ungültiger Motorindex zum Stoppen:", repr(axis))
        raise ValueError("Ungültiger Motorindex zum Stoppen")
    print("Stop Event gesetzt")


def cleanup():
    global h
    if h is None:
        return

    for pins in MOTOR_PINS.values():
        try:
            lgpio.gpio_write(h, pins["ENA"], 1)
            lgpio.gpio_write(h, pins["DIR"], 0)
        except Exception:
            pass

    try:
        lgpio.gpiochip_close(h)
    except Exception:
        pass

    h = None
    print("GPIOs freigegeben")
