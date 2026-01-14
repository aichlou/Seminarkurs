import RPi.GPIO as GPIO
import time

ENA = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ENA, GPIO.OUT)

GPIO.output(ENA, GPIO.LOW)
time.sleep(2)
GPIO.output(ENA, GPIO.HIGH)