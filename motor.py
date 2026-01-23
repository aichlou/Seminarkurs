import time
import threading
import lgpio
stop_event = threading.Event()
h = None

def setup_motors():
    global h
    h = lgpio.gpiochip_open(0)
    for motor in range(2):
        if motor == 0:
            PUL = 8
            DIR = 10
            ENA = 12
        elif motor == 1:
            PUL = 11
            DIR = 13
            ENA = 15
        else :
            print("Ungültiger Motorindex:", repr(motor))
            raise ValueError("Ungültiger Motorindex")
        lgpio.gpio_claim_output(h, PUL, 0)
        lgpio.gpio_claim_output(h, DIR, 0)
        lgpio.gpio_claim_output(h, ENA, 0)
        lgpio.gpio_write(h, ENA, 0)
        lgpio.gpio_write(h, DIR, 1)
def rotate(motor, speed):
    print("DEBUG:", type(motor), repr(motor))
    if motor == "X":
        print("Hallo")
        PUL = 8
        DIR = 10
        ENA = 12
    elif motor == "Y":
        PUL = 11
        DIR = 13
        ENA = 15
    else:
        print("Ungültiger Motorindex:", repr(motor))
        raise ValueError("Ungültiger Motorindex")
    if(speed < 0):
        lgpio.gpio_write(h, DIR, 0)
        speed = -speed
    print(f"Starte Motor {motor} mit Geschwindigkeit {speed}")
    while not stop_event.is_set():
        pause = ((10-speed)**0.5)/10 + 0.0001
        lgpio.gpio_write(h, ENA, 0)
        for _ in range(200000):
            lgpio.gpio_write(h, PUL, 1)
            time.sleep(pause)
            lgpio.gpio_write(h, PUL, 0)
            time.sleep(pause)
        lgpio.gpio_write(h, ENA, 1)
    print("Motor gestoppt")
    lgpio.gpio_write(h, ENA, 1)
    lgpio.gpio_write(h, DIR, 0)


def stop_motor():
    stop_event.set()