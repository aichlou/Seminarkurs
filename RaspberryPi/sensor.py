import lgpio
import time

SENSOR_PINS = [20, 21, 19, 26, 13, 6, 10] #9
DISTANCE_SENSOR_INDEX = 6
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
    
    # Warte kurz und initialisiere alle aktuellen Sensor-States
    print("Sensor-Thread: Warte 0.2s vor initialer Sensor-Erfassung...")
    time.sleep(0.2)
    
    for index, pin in enumerate(SENSOR_PINS):
        if index == DISTANCE_SENSOR_INDEX:
            # Distanzsensor
            dist = distance(h)
            if dist is not None:
                distance_state = dist < 5
                last_states[DISTANCE_SENSOR_INDEX] = distance_state
                if distance_state:
                    print(f"Sensor-Thread: Initial - Sensor an Pin {SENSOR_PINS[DISTANCE_SENSOR_INDEX]} (Index {DISTANCE_SENSOR_INDEX}) ist ON")
                    commands.put(("change_state", DISTANCE_SENSOR_INDEX, True))
            else:
                last_states[DISTANCE_SENSOR_INDEX] = False
        else:
            # Digitale Sensoren
            raw_state = lgpio.gpio_read(h, pin)
            state = not raw_state if pin in INVERT_PINS else raw_state
            last_states[index] = state
            if state:
                print(f"Sensor-Thread: Initial - Sensor an Pin {pin} (Index {index}) ist ON")
                commands.put(("change_state", index, True))
    
    try:
        while True:
            dist = distance(h)
            if dist is not None:
                distance_state = dist < 5
                if distance_state != last_states[DISTANCE_SENSOR_INDEX]:
                    print(f"Sensor an Pin {SENSOR_PINS[DISTANCE_SENSOR_INDEX]} (Index {DISTANCE_SENSOR_INDEX}) hat sich geändert zu {distance_state}")
                    commands.put(("change_state", DISTANCE_SENSOR_INDEX, distance_state))
                    last_states[DISTANCE_SENSOR_INDEX] = distance_state

            for index, pin in enumerate(SENSOR_PINS):
                if index == DISTANCE_SENSOR_INDEX:
                    continue

                raw_state = lgpio.gpio_read(h, pin)
                state = not raw_state if pin in INVERT_PINS else raw_state
                if state != last_states[index]:
                    print(f"Sensor an Pin {pin} (Index {index}) hat sich geändert zu {state}")
                    commands.put(("change_state", index, state))
                    last_states[index] = state

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


