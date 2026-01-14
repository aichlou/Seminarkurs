import time
import webserver

try:
    import RPi.GPIO as GPIO
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

'''
PUL = 11
DIR = 13
ENA = 15 '''

PUL = 8
DIR = 10
ENA = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PUL, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.output(ENA, GPIO.LOW)
GPIO.output(DIR, GPIO.HIGH)

for _ in range(200000):
    GPIO.output(PUL, GPIO.HIGH)
    time.sleep(0.0001)
    GPIO.output(PUL, GPIO.LOW)
    time.sleep(0.0001)

GPIO.output(ENA, GPIO.HIGH)