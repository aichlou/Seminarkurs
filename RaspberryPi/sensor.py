import lgpio
import time

SENSOR_PINS = [20, 21, 19, 26, 13, 2]
INVERT_PINS = [20, 21]


def read_sensors(commands):
    print("Starte Sensor-Lesefunktion")
    h = lgpio.gpiochip_open(0)
    for pin in SENSOR_PINS:
        lgpio.gpio_claim_input(h, pin, lgpio.SET_PULL_UP)

    last_states = [None] * len(SENSOR_PINS)

    while True:
        for index, pin in enumerate(SENSOR_PINS):
            raw_state = lgpio.gpio_read(h, pin)
            state = not raw_state if pin in INVERT_PINS else raw_state
            if last_states[index] is None:
                last_states[index] = state
                continue

            if state != last_states[index]:
                print(f"Sensor an Pin {pin} (Index {index}) hat sich geändert zu {state}")
                commands.put(("change_state", index, state))
                last_states[index] = state

        time.sleep(0.01)
