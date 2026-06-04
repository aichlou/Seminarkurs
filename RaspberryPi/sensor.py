import lgpio
import time
import threading

def read_sensors(commands):
    print("Starte Sensor-Lesefunktion")
    h = lgpio.gpiochip_open(0)
    SENSOR_PINS = [21, 26]
    for pin in SENSOR_PINS:
        lgpio.gpio_claim_input(h, pin)
    states = [False] * len(SENSOR_PINS)
    last_states = [False] * len(SENSOR_PINS)
    while True:
        for pin in SENSOR_PINS:
            state = lgpio.gpio_read(h, pin)
            if (state != last_states[SENSOR_PINS.index(pin)]):
                print(f"Sensor an Pin {pin}, mit dem Index {SENSOR_PINS.index(pin)} hat sich geändert zu {state}")
                commands.put(("change_state", SENSOR_PINS.index(pin), state))
            last_states[SENSOR_PINS.index(pin)] = state