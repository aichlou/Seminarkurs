import lgpio
import time
import threading

def read_sensors(commands):
    h = lgpio.gpiochip_open(0)
    SENSOR_PINS = [21]
    for pin in SENSOR_PINS:
        lgpio.gpio_claim_input(h, pin)
    states = [False] * len(SENSOR_PINS)

    last_states = [False] * len(SENSOR_PINS)
    while True:
        for pin in SENSOR_PINS:
            state = lgpio.gpio_read(h, pin)
            if (state != last_states[SENSOR_PINS[pin]]):
                print(f"Sensor an Pin {pin} hat sich geändert zu {state}")
                index = 0
                match state:
                    case 21:
                        index = 1
                    case _:
                        index = 0
                commands.put(("change_state", index, state))
            last_states[SENSOR_PINS] = state