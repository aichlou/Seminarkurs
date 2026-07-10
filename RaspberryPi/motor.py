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
}

Z_NEG_PIN = 2
Z_POS_PIN = 3

STATION_PINS = {"A": 9, "B": 11}

POS = {
    "X": 0,
    "Y": 0,
    "Z": 0
}

WEB_STATUS_URL = 'http://127.0.0.1:5000/status'
LOCAL_ISSET_URL = 'http://127.0.0.1:5001/isset'


def local_isset_check(timeout=2):
    """Prüft /isset auf localhost:5001 und gibt True/False zurück."""
    try:
        with urllib.request.urlopen(LOCAL_ISSET_URL, timeout=timeout) as response:
            body = response.read().decode().strip()
        print(f"motor.local_isset_check: got '{body}' from {LOCAL_ISSET_URL}")
        return body == 'YES'
    except Exception as exc:
        print(f"motor.local_isset_check: {exc}")
        return False


def temp():
    print("motor.temp: starting homing sequence")
    print("motor.temp: calling zMotor(1)")
    zMotor(-1)
    print("motor.temp: calling zMotor(0)")
    zMotor(0)
    print("motor.temp: calling zMotor(-1)")
    zMotor(-1)
    print("motor.temp: calling zMotor(0)")
    zMotor(0)

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
    zMotor(0)
    pos(-1, True)
    zMotor(1)
    station_einlagern()
    pos(-1, False)
    zMotor(0)
    pos(addr, False)
    zMotor(-1)
    pos(addr, True)
    zMotor(0)
    
def ret(addr):
    print("Motor Thread ist Ready für Returen des Elements")
    zMotor(0)
    pos(addr, True)
    zMotor(-1)
    pos(addr, False)
    zMotor(0)
    pos(-1, False)
    zMotor(1)
    station(True)
    pos(-1, True)
    station_auslagern()
    zMotor(0)

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
        
def station_testen():
    station_einlagern()
    time.sleep(2)
    station_auslagern()        
        
def station_einlagern():
    print("Beginne Station einlagern")
    station(True, True)
    while local_isset_check():
        time.sleep(0.3)
    time.sleep(6)
    station(False)
    
def station_auslagern():
    print("Beginne Station auslagern")
    station(True)
    while not local_isset_check():
        time.sleep(0.3)
    station(False)
    
def zMotor(goto, sensor = False):
    print(f"zMotor: called with goto={goto!r}, sensor={sensor}, current Z={POS['Z']}")
    if goto not in (-1, 0, 1):
        print(f"zMotor: Ungültiger goto-Wert {goto!r}; erwartete -1, 0 oder 1")
        return

    setup_motors()
    handle = get_handle()
    try:
        if goto == 0:
            s4, s5 = SensorZ()
            print(f"zMotor: goto=0 requested, sensor initial values: 4={s4}, 5={s5}")
            if not s4 and s5:
                print("zMotor: falscher Sensor ist an, weitermachen.")
                #return
            if s4 and not  s5:
                print("zMotor: Sensor 4 aktiv, 5 nicht, Z bereits in der Mitte.")
                POS["Z"] = 0
                return

            if POS["Z"] > 0:
                print("zMotor: POS[Z] > 0, fahre Richtung -1 bis Mitte erreicht")
                return zMotor(-1, sensor=True)
            elif POS["Z"] < 0:
                print("zMotor: POS[Z] < 0, fahre Richtung 1 bis Mitte erreicht")
                return zMotor(1, sensor=True)
            else:
                print("zMotor: POS[Z] == 0, Sensoren signalisieren nicht Mitte; fahre Richtung - 1 mit Sensorüberwachung")
                return zMotor(-1, sensor=True)

        # goto == -1 oder goto == 1
        if goto == -1:
            print("zMotor: starte Bewegung in Richtung -1 (Pin 2 HIGH, Pin 3 LOW)")
            lgpio.gpio_write(handle, Z_NEG_PIN, 1)
            lgpio.gpio_write(handle, Z_POS_PIN, 0)
        else:
            print("zMotor: starte Bewegung in Richtung 1 (Pin 2 LOW, Pin 3 HIGH)")
            lgpio.gpio_write(handle, Z_NEG_PIN, 0)
            lgpio.gpio_write(handle, Z_POS_PIN, 1)

        if sensor:
            print("zMotor: Sensor-Modus aktiv, stoppe sobald Sensor 4 aktiv ist")
            steps = 0
            while True:
                s4, s5 = SensorZ()
                print(f"zMotor: sensor loop step={steps} sensor4={s4} sensor5={s5}")
                if s4 and not s5:
                    print("zMotor: Sensor 4 aktiv und Sensor 5 deaktiv (Mitte erreicht), stoppe Z-Motor")
                    POS["Z"] = 0
                    break
                steps += 1
                if steps > 500:
                    print("zMotor: Sensor-Modus Timeout nach 500 Versuchen")
                    break
                time.sleep(0.05)
        else:
            duration = 15.5
            print(f"zMotor: Zeitorientierte Bewegung, Dauer={duration}s")
            time.sleep(duration)
            if goto == -1:
                POS["Z"] -= 1
            else:
                POS["Z"] += 1
            print(f"zMotor: Bewegung abgeschlossen, neuer POS[Z]={POS['Z']}")

    except Exception as e:
        print(f"Fehler in zMotor: {e}")
    finally:
        lgpio.gpio_write(handle, Z_NEG_PIN, 0)
        lgpio.gpio_write(handle, Z_POS_PIN, 0)
        print("zMotor: Z-Motor angehalten")

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
