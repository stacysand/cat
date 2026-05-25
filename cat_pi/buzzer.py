import lgpio
import time

PIN = 18
FREQ = 2000      # Hz — try 1000–4000, higher = more piercing
DURATION = 1.0   # seconds

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, PIN)

period = 1.0 / FREQ
cycles = int(DURATION * FREQ)

for _ in range(cycles):
    lgpio.gpio_write(h, PIN, 1)
    time.sleep(period / 2)
    lgpio.gpio_write(h, PIN, 0)
    time.sleep(period / 2)

lgpio.gpiochip_close(h)
