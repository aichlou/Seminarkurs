import time
import threading
try:
    import RPi.GPIO as GPIO  # type: ignore
except (ImportError, RuntimeError):
    class GPIO:
        BOARD = "BOARD"
        OUT = "OUT"
        LOW = 0
        HIGH = 1

        @staticmethod
        def setmode(mode):
            print(f"[MOCK GPIO] setmode({mode})")

        @staticmethod
        def setup(pin, mode):
            print(f"[MOCK GPIO] setup(pin={pin}, mode={mode})")

        @staticmethod
        def output(pin, state):
            print(f"[MOCK GPIO] output(pin={pin}, state={state})")

stop_event = threading.Event()

def setup_motors():
    GPIO.setmode(GPIO.BOARD)
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
        GPIO.setup(PUL, GPIO.OUT)
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(ENA, GPIO.OUT)
        GPIO.output(ENA, GPIO.LOW)
        GPIO.output(DIR, GPIO.HIGH)

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
        GPIO.output(DIR, GPIO.HIGH)
        speed = -speed
    print(f"Starte Motor {motor} mit Geschwindigkeit {speed}")
    while not stop_event.is_set():
        pause = ((10-speed)**0.5)/10 + 0.0001
        GPIO.output(ENA, GPIO.LOW)
        for _ in range(200000):
            GPIO.output(PUL, GPIO.HIGH)
            time.sleep(pause)
            GPIO.output(PUL, GPIO.LOW)
            time.sleep(pause)
        GPIO.output(ENA, GPIO.HIGH)
    print("Motor gestoppt")
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(DIR, GPIO.LOW)


def stop_motor():
    stop_event.set()