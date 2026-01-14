import RPi.GPIO as GPIO
import time

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