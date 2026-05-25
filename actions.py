import requests
import threading
import time

# def trigger_function():
#     requests.get("http://192.168.1.173:5000/buzz")
#     print("THE CAT IS IN THE AREA")

_last_triggered = 0
_COOLDOWN = 3.0  # seconds — tune to buzzer duration + silence gap
_lock = threading.Lock()

def trigger_function():
    global _last_triggered
    
    now = time.monotonic()
    
    with _lock:
        if now - _last_triggered < _COOLDOWN:
            return  # still in cooldown, skip
        _last_triggered = now
    
    # fire and forget — never blocks the main loop
    threading.Thread(
        target=_send_buzz,
        daemon=True
    ).start()

def _send_buzz():
    try:
        requests.get("http://192.168.1.173:5000/buzz", timeout=2)
        print("THE CAT IS IN THE AREA")
    except requests.exceptions.RequestException as e:
        print(f"Buzz request failed: {e}")
