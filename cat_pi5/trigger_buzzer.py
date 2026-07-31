import requests
import threading
import time

from config import COOLDOWN_SECONDS, HTTP_ADDRESS, HTTP_PRINT

last_triggered = 0
lock = threading.Lock()

# create thread
def trigger_buzzer_pi2_via_server():
    
    # timing
    global last_triggered
    now = time.monotonic()
    with lock:
        if now - last_triggered < COOLDOWN_SECONDS:
            return  # still in cooldown, skip
        last_triggered = now
    
    # fire and forget — never blocks the main loop
    threading.Thread(
        target=send_buzz,
        daemon=True
    ).start()

# implement buzzling
def send_buzz():
    try:
        requests.get(HTTP_ADDRESS, timeout=2)
        print(HTTP_PRINT)
    except requests.exceptions.RequestException as e:
        print(f"Buzz request failed: {e}")
