import time
import lgpio

ENA = 22  # Enable
PUL = 17  # Puls/Step Pin (musst du anpassen!)

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, ENA)
lgpio.gpio_claim_output(h, PUL)

print("Motor läuft...")

# Motor aktivieren
lgpio.gpio_write(h, ENA, 0)

# Schritte fahren
for _ in range(20000):
    lgpio.gpio_write(h, PUL, 1)
    time.sleep(0.0002)
    lgpio.gpio_write(h, PUL, 0)
    time.sleep(0.0002)

# Motor deaktivieren
lgpio.gpio_write(h, ENA, 1)
print("Fertig")