import time
import threading
import lgpio
import sys
import math
import urllib.request
import json

stop_event_x = threading.Event()
stop_event_y = threading.Event()
stop_event_z = threading.Event()
h = None

MOTOR_PINS = {
    "X": {"PUL": 14, "DIR": 15, "ENA": 18},
    "Y": {"PUL": 17, "DIR": 27, "ENA": 22},
    "Z": {"PUL": 2, "DIR": 3, "ENA": None},
}

STATION_PINS = {"A": 9, "B": 11}

POS = {
    "X": 0,
    "Y": 0,
    "Z": 0
}

WEB_STATUS_URL = 'http://127.0.0.1:5000/status'

def temp():
    zMotor(1)
    zMotor(-0.3)

def pos(addr, down):
    row = math.floor(int(addr) / 10) - 1
    column = 5 - int(str(addr)[1:])
    Xcoord = 1100 + column * 1500
    Ycoord = 0
    match row:
        case 0 | 1 | 2:
            Ycoord = row * 2300 - 600
        case 3:
            Ycoord = 6200
        case 4:
            Ycoord = 8450
        case _:
            Ycoord = 0
            print("ALLLLARMMMMM Colum hat keinen Richtiigen Wert ALLLARMMM")
    if addr == -1:
        Xcoord = 7170
        Ycoord = -920
    if down:
        Ycoord = Ycoord -350
    print(Xcoord)
    print(Ycoord)
    goto("X", Xcoord)
    goto("Y", Ycoord)
      
def send(addr):
    print("Motor Thread ist Ready für Senden des Elements")
    #Z-Achse in Mitte
    pos(-1, True)
    #Z-Achse nach hinten
    pos(-1, False)
    #Z-Achse in die Mitte
    pos(addr, False)
    #Z-Achse nach vorne
    pos(addr, True)
    # Z-Achse in die Mitte
    
def ret(addr):  
    print("Motor Thread ist Ready für Returen des Elements")
    #Z-Achse in Mitte
    pos(addr, True)
    # Z-Achse nach Vorne
    pos(addr, False)
    # Z-Achse in Mitte
    pos(-1, False)
    # Z-Achse nach Hinten
    pos(-1, True)
    # Z-Achse in die Mitte

def get_Pos(axis):
    return POS[axis]

def get_handle():
    global h
    if h is None:
        h = lgpio.gpiochip_open(0)
    return h

def station(spin, direction = False):
    handle = get_handle()
    a_pin = STATION_PINS.get("A")
    b_pin = STATION_PINS.get("B")
    if spin:
        if direction:
            if a_pin is not None: lgpio.gpio_write(handle, a_pin, 1)
            if b_pin is not None: lgpio.gpio_write(handle, b_pin, 0)
        else:
            if a_pin is not None: lgpio.gpio_write(handle, a_pin, 0)
            if b_pin is not None: lgpio.gpio_write(handle, b_pin, 1)
    else:
        if a_pin is not None: lgpio.gpio_write(handle, a_pin, 0)
        if b_pin is not None: lgpio.gpio_write(handle, b_pin, 0)

def zMotor(goto, sensor = False):
    setup_motors()
    handle = get_handle()
    z_pins = MOTOR_PINS.get("Z", {})
    pul = z_pins.get("PUL")
    dir_pin = z_pins.get("DIR")
    try:
        # Special case: goto == 0 -> move to middle until both sensors 4 & 5 are True
        if goto == 0:
            # decide direction bit consistent with `rotate()` (1 -> decrement POS)
            dir_bit = 0 if POS["Z"] < 0 else 1
            if dir_pin is not None:
                lgpio.gpio_write(handle, dir_pin, dir_bit)

            if pul is None:
                print("zMotor: Kein PUL-Pin für Z-Achse definiert")
                return

            max_steps = 2000
            steps = 0
            while steps < max_steps:
                # Pulse once
                lgpio.gpio_write(handle, pul, 1)
                time.sleep(0.01)
                lgpio.gpio_write(handle, pul, 0)
                time.sleep(0.01)

                # update POS similar to rotate()
                POS["Z"] = POS["Z"] - ((dir_bit * 2) - 1)

                s4, s5 = SensorZ()
                print(f"zMotor: step={steps} POS[Z]={POS['Z']} sensor4={s4} sensor5={s5}")
                if s4 and s5:
                    print("zMotor: Mitte erreicht, beide Sensoren aktiv.")
                    break
                steps += 1

            if steps >= max_steps:
                print("zMotor: Max steps reached while homing Z; sensors not both True")
            return

        # Non-zero goto: simple timed move (keeps previous behaviour)
        if goto < 0:
            # negative -> move in negative direction pin pattern
            if dir_pin is not None: lgpio.gpio_write(handle, dir_pin, 1)
        else:
            if dir_pin is not None: lgpio.gpio_write(handle, dir_pin, 0)

        mag = abs(goto)
        if pul is not None:
            # perform pulses proportional to mag (simple approximation)
            # here mag is treated as seconds; keep previous semantics
            if goto < 0:
                POS["Z"] -= mag
                time.sleep(mag)
            else:
                POS["Z"] += mag
                time.sleep(mag)

    except Exception as e:
        print(f"Fehler in zMotor: {e}")
    finally:
        if dir_pin is not None: lgpio.gpio_write(handle, dir_pin, 0)
        if pul is not None: lgpio.gpio_write(handle, pul, 0)

def SensorZ():
    try:
        with urllib.request.urlopen(WEB_STATUS_URL, timeout=2) as response:
            raw = response.read().decode()
        try:
            status = json.loads(raw)
        except json.JSONDecodeError as err:
            print(f"SensorZ: JSON-Decode-Fehler: {err}; raw={raw!r}")
            return (None, None)

        if not isinstance(status, list):
            print(f"SensorZ: Status ist kein Liste, sondern {type(status).__name__}: {status!r}")
            return (None, None)

        if len(status) <= 5:
            print(f"SensorZ: Status-Liste zu kurz ({len(status)}): {status!r}")
            return (None, None)

        sensor_4 = status[4]
        sensor_5 = status[5]
        print(f"SensorZ: status[4]={sensor_4!r}, status[5]={sensor_5!r}")
        return (bool(sensor_4), bool(sensor_5))
    except Exception as exc:
        print(f"SensorZ: Fehler beim Abruf des Status: {exc}")
        return (None, None)
    

def set_null():
    POS["X"] = 0
    POS["Y"] = 0

def setup_motors():
    global h
    if h is not None:
        try:
            lgpio.gpiochip_close(h)
        except Exception:
            pass
    h = lgpio.gpiochip_open(0)

    for axis, pins in MOTOR_PINS.items():
        pul = pins.get("PUL")
        dir_pin = pins.get("DIR")
        ena = pins.get("ENA")
        if pul is not None:
            lgpio.gpio_claim_output(h, pul, 0)
        if dir_pin is not None:
            lgpio.gpio_claim_output(h, dir_pin, 0)
        if ena is not None:
            lgpio.gpio_claim_output(h, ena, 0)
            lgpio.gpio_write(h, ena, 1)

    # Claim station pins if present
    for pin in STATION_PINS.values():
        try:
            lgpio.gpio_claim_output(h, pin, 0)
            lgpio.gpio_write(h, pin, 0)
        except Exception:
            pass
    lgpio.gpio_claim_output(h, 2, 0)
    lgpio.gpio_claim_output(h, 3, 0)
    lgpio.gpio_claim_output(h, 9, 0)
    lgpio.gpio_claim_output(h, 11, 0)

def goto(axis, target):
    pos = get_Pos(axis)
    if pos > target:
        rotate(axis, -0.4, target)
    elif pos < target:
        rotate(axis, 0.4, target)

def rotate(axis, speed, border = None):
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
        ena = pins.get("ENA")
        if ena is not None:
            lgpio.gpio_write(handle, ena, 1)
        print(f"Motor {axis} wurde nicht gestartet: Geschwindigkeit ist 0")
        return

    direction = 1 if speed < 0 else 0
    dir_pin = pins.get("DIR")
    pul_pin = pins.get("PUL")
    ena = pins.get("ENA")
    if dir_pin is not None:
        lgpio.gpio_write(handle, dir_pin, direction)
    if ena is not None:
        lgpio.gpio_write(handle, ena, 0)
    speed = abs(speed)
    pause = 1 / (40 * (speed + 10))

    print(f"Starte Motor {axis} mit Geschwindigkeit {speed}, Richtung {direction}")
    try:
        while not stop_event.is_set():
            if pul_pin is None:
                print(f"Kein PUL-Pin für Motor {axis}, breche Drehung ab")
                break
            lgpio.gpio_write(handle, pul_pin, 1)
            time.sleep(pause)
            lgpio.gpio_write(handle, pul_pin, 0)
            time.sleep(pause)
            POS[axis] = POS[axis] - ((direction * 2) - 1)
            if border is not None and border == POS[axis]:
                stop_event.set()
    except Exception as exc:
        print("Fehler beim Drehen des Motors:", exc)
    finally:
        if ena is not None:
            lgpio.gpio_write(handle, ena, 1)
        if dir_pin is not None:
            lgpio.gpio_write(handle, dir_pin, 0)
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
            ena = pins.get("ENA")
            dir_pin = pins.get("DIR")
            if ena is not None:
                lgpio.gpio_write(h, ena, 1)
            if dir_pin is not None:
                lgpio.gpio_write(h, dir_pin, 0)
        except Exception:
            pass

    # Reset station pins
    for pin in STATION_PINS.values():
        try:
            lgpio.gpio_write(h, pin, 0)
        except Exception:
            pass

    try:
        lgpio.gpiochip_close(h)
    except Exception:
        pass

    h = None
    print("GPIOs freigegeben")

def cli():
    """Einfache CLI für Motor-Kontrolle"""
    print("=== Motor Control CLI ===")
    print("Befehle: get_pos, set_null, setup, rotate, stop, cleanup, exit, goto, pos, zmot")
    print()
    
    while True:
        try:
            command = input("> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0]
            
            if cmd == "zmot":
                zMotor(float(command[1]))

            elif cmd == "get_pos":
                if len(command) < 2:
                    print("Fehler: get_pos <axis> (z.B. get_pos X)")
                    continue
                print(get_Pos(command[1]))
            elif cmd == "station":
                station(int(command[1]))
            elif cmd == "pos":
                pos(int(command[1]))
            
            elif cmd == "set_null":
                set_null()
            
            elif cmd == "setup":
                setup_motors()
            
            elif cmd == "rotate":
                if len(command) < 3:
                    print("Fehler: rotate <axis> <speed> [border]")
                    print("Beispiel: rotate X 100 oder rotate X 100 1000")
                    continue
                axis = command[1]
                speed = float(command[2])
                border = int(command[3]) if len(command) > 3 else None
                try:
                    rotate(axis, speed, border)
                except KeyboardInterrupt:
                    print("\nAbgebrochen!")
            
            elif cmd == "stop":
                if len(command) < 2:
                    print("Fehler: stop <axis> (z.B. stop X)")
                    continue
                stop_motor(command[1])
            
            elif cmd == "cleanup":
                cleanup()
            
            elif cmd == "exit" or cmd == "quit":
                print("Auf Wiedersehen!")
                break
            
            elif cmd == "goto":
                if len(command) < 3:
                    print("Fehler: goto <axis> <target>")
                    continue
                axis = command[1].upper()
                target = int(command[2])
                goto(axis, target)
            
            else:
                print(f"Unbekannter Befehl: {cmd}")
        
        except ValueError as e:
            print(f"Fehler bei der Eingabe: {e}")
        except KeyboardInterrupt:
            print("\nAbgebrochen")
            break
        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    cli()
