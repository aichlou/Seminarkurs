import lgpio
import time

# Chip öffnen (0 ist typisch der erste GPIO-Chip)
h = lgpio.gpiochip_open(0)

# GPIO Pin 2 als Eingabe mit Pull-down Widerstand konfigurieren
pin = 2
lgpio.gpio_claim_input(h, pin, lgpio.SET_PULL_DOWN)

try:
    while True:
        # Pin-Zustand auslesen
        state = lgpio.gpio_read(h, pin)
        
        # Zustand im Terminal ausgeben
        print(f"GPIO Pin {pin}: {state} ({'HIGH' if state else 'LOW'})")
        
        # Kurze Verzögerung (1 Sekunde)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgramm beendet")
    
finally:
    # Ressourcen freigeben
    lgpio.gpiochip_close(h)
