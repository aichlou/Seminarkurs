import lgpio
import time

SENSOR_PINS = [20, 21, 19, 26, 13, 6, 10] #9
INVERT_PINS = [20, 21]
TRIG_PIN = 5
ECHO_PIN = 0


def read_sensors(commands):
    print("Starte Sensor-Lesefunktion")
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, TRIG_PIN)
    lgpio.gpio_claim_input(h, ECHO_PIN)
    for pin in SENSOR_PINS:
        lgpio.gpio_claim_input(h, pin, lgpio.SET_PULL_UP)

    last_states = [None] * len(SENSOR_PINS)
    try:
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
                    
            dist = distance(h)
            if dist is not None:
                print(dist)

            time.sleep(0.01)   
    except KeyboardInterrupt:
        print("Beendet")
    finally:
        lgpio.gpiochip_close(h)

def distance(h):
    try:
        lgpio.gpio_write(h, TRIG_PIN, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(h, TRIG_PIN, 0)
        
        start = None
        end = None
        
        timeout = time.time() + 0.1
        while lgpio.gpio_read(h, ECHO_PIN) == 0 and time.time() < timeout:
            start = time.time()
        
        timeout = time.time() + 0.1
        while lgpio.gpio_read(h, ECHO_PIN) == 1 and time.time() < timeout:
            end = time.time()
        
        if start is None or end is None:
            return None
        
        elapsed = end - start
        distance_cm = (elapsed * 34300) / 2
        
        return distance_cm
    except Exception as e:
        return None


