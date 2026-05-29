import time
import threading
# from ld import motor
import lgpio
stop_event_x = threading.Event()
stop_event_y = threading.Event()
h = None

def setup_motors():
    global h
    if h is not None:
        try:
            lgpio.gpiochip_close(h)
        except:
            pass
    h = lgpio.gpiochip_open(0)
    for motor in range(2):
        if motor == 0:
            PUL = 14  # Pin 8  → GPIO14
            DIR = 15  # Pin 10 → GPIO15
            ENA = 18  # Pin 12 → GPIO18
        elif motor == 1:
            PUL = 17  # Pin 11 → GPIO17
            DIR = 27  # Pin 13 → GPIO27
            ENA = 22  # Pin 15 → GPIO22
        else :
            print("Ungültiger Motorindex:", repr(motor))
            raise ValueError("Ungültiger Motorindex")
        lgpio.gpio_claim_output(h, PUL, 0)
        lgpio.gpio_claim_output(h, DIR, 0)
        lgpio.gpio_claim_output(h, ENA, 0)
        lgpio.gpio_write(h, ENA, 0)
        lgpio.gpio_write(h, DIR, 1)
def rotate(motor, speed):
    if motor == "X":
        stop_event_x.clear()
    elif motor == "Y":
        stop_event_y.clear()
    print("DEBUG:", type(motor), repr(motor))
    if motor == "X":
        PUL = 14  # Pin 8  → GPIO14
        DIR = 15  # Pin 10 → GPIO15
        ENA = 18  # Pin 12 → GPIO18
    elif motor == "Y":
        PUL = 17  # Pin 11 → GPIO17
        DIR = 27  # Pin 13 → GPIO27
        ENA = 22  # Pin 15 → GPIO22
    else:
        print("Ungültiger Motorindex:", repr(motor))
        raise ValueError("Ungültiger Motorindex")
    if(speed < 0):
        lgpio.gpio_write(h, DIR, 1)
        speed = -speed
    else:
        lgpio.gpio_write(h, DIR, 0)
    print(f"Starte Motor {motor} mit Geschwindigkeit {speed}")
    stop_event = stop_event_x if motor == "X" else stop_event_y
    while not stop_event.is_set():
        pause = 1 / (100* (speed + 7))
        print(f"DEBUG: Geschwindigkeit {speed} ergibt Pause {pause}")
        print("Richtwert für Pause ist 0.0002")
        lgpio.gpio_write(h, ENA, 0)
        
        for step in range(200000):
            if stop_event.is_set():
                print("Stop Event erkannt, Motor wird gestoppt")
                break
            lgpio.gpio_write(h, PUL, 1)
            time.sleep(pause)
            lgpio.gpio_write(h, PUL, 0)
            time.sleep(pause)
        
        lgpio.gpio_write(h, ENA, 1)
    print("Motor gestoppt")
    lgpio.gpio_write(h, ENA, 0)
    lgpio.gpio_write(h, DIR, 0)


def stop_motor(motor):
    if motor == "X":
        stop_event_x.set()
    elif motor == "Y":
        stop_event_y.set()
    else:
        print("Ungültiger Motorindex zum Stoppen:", repr(motor))
        raise ValueError("Ungültiger Motorindex zum Stoppen")
    #ENA muss noch auf 1 gesetzt werden
    print("Stop Event gesetzt")



def cleanup():
    global h
    lgpio.gpiochip_write(18, 0)
    lgpio.gpiochip_write(22, 0)
    lgpio.gpiochip_close(h)
    print("GPIOs freigegeben")

    
