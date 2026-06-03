import time
import lgpio

ENA = 14  # Enable
PUL = 18  # Puls/Step Pin (musst du anpassen!)
DIR = 15

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, ENA)
lgpio.gpio_claim_output(h, PUL)
lgpio.gpio_claim_output(h, DIR)

print("Motor läuft...")

# Motor aktivieren
lgpio.gpio_write(h, ENA, 0)
lgpio.gpio_write(h, DIR, 0)

# Schritte fahren
for _ in range(20000):
    lgpio.gpio_write(h, PUL, 1)
    time.sleep(0.005)
    lgpio.gpio_write(h, PUL, 0)
    time.sleep(0.005)

# Motor deaktivieren
lgpio.gpio_write(h, ENA, 1)
print("Fertig")
