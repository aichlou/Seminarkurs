import time
import threading
import lgpio
import sys
import math

stop_event_x = threading.Event()
stop_event_y = threading.Event()
stop_event_z = threading.Event()
h = None

MOTOR_PINS = {
    "X": {"PUL": 14, "DIR": 15, "ENA": 18},
    "Y": {"PUL": 17, "DIR": 27, "ENA": 22},
}

POS = {
    "X": 0,
    "Y": 0,
}

def pos(addr, down):
    row = math.floor(addr / 10) - 1
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
        lgpio.gpio_claim_output(h, pins["PUL"], 0)
        lgpio.gpio_claim_output(h, pins["DIR"], 0)
        lgpio.gpio_claim_output(h, pins["ENA"], 0)
        lgpio.gpio_write(h, pins["ENA"], 1)

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
            POS[axis] = POS[axis] - ((direction * 2) - 1)
            if border is not None and border == POS[axis]:
                stop_event.set()
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

def cli():
    """Einfache CLI für Motor-Kontrolle"""
    print("=== Motor Control CLI ===")
    print("Befehle: get_pos, set_null, setup, rotate, stop, cleanup, exit, goto, pos")
    print()
    
    while True:
        try:
            command = input("> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0]
            
            if cmd == "get_pos":
                if len(command) < 2:
                    print("Fehler: get_pos <axis> (z.B. get_pos X)")
                    continue
                print(get_Pos(command[1]))
            
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
