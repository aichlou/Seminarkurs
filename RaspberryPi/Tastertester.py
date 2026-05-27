import RPI.GPIO as GPIO
import time

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    state = GPIO.input(pin)
    print(state)
    time.sleep(0.1)