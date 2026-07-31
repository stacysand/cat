import numpy as np

# --------------------  detection  --------------------

# model for detection
MODEL_NAME = "yolov8n.pt"

# roi (masked) (as a pollygon) e.g., for the floor on the kitchen
ROI = np.array([
    [500, 380],  # top-left
    [810, 400],  # top-right
    [750, 710],  # bottom-right
    [150, 710],  # bottom-left
], dtype=np.int32)

# target
TARGET_CLASSES = ('cat', 'dog')  
#TARGET_CLASSES = ('person',) # for testing

# --------------------  triggered functions  --------------------

# save_frames and trigger_buzzer: how long to wait before next round
COOLDOWN_SECONDS = 3.0

# save_frames: how many to keep so the Pi's SD card doesn't slowly fill up
MAX_SAVED_FRAMES = 300

# save_frames: where the frames get saved
DIR_DETECTIONS = "./detections"
DIR_CLEAN_FRAMES = "./detections/clean_frames"

# trigger_buzzer: send requiest for buzzling
HTTP_ADDRESS = "http://192.168.1.173:5000/buzz"

# trigger_buzzer: sent request confirmation printing
HTTP_PRINT = "THE CAT IS IN THE AREA! Sent buzzling requiest to Pi2."

# --------------------  stream  --------------------

# streaming RTSP
RTSP_URL = "rtsp://192.168.1.173:8554/cam"

# seconds the picture is allowed to stay exactly the same before called "stuck"
STALE_TIMEOUT = 8

# consecutive failed reconnect attempts before give up and let systemd restart
MAX_RECONNECTS = 5
