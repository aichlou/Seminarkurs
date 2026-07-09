import lgpio
import time

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, 2) #9
lgpio.gpio_claim_output(h, 3) # 11

while True:
    try:
        lgpio.gpio_write(h, 2, 0)
        lgpio.gpio_write(h, 3, 1)
        time.sleep(2)
        lgpio.gpio_write(h, 2, 1)
        lgpio.gpio_write(h, 3, 0)
        time.sleep(2)
    except KeyboardInterrupt:
        lgpio.gpio_write(h, 2, 0)
        lgpio.gpio_write(h, 3, 0)
        break
