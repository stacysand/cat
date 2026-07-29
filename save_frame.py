import os
import cv2
from datetime import datetime
import time

# where the "what did the model actually see" frames get saved
dir_detections = "./detections"
dir_clean_frames = "./detections/clean_frames"

# cap how many to keep so the Pi's SD card doesn't slowly fill up
MAX_SAVED_FRAMES = 300
os.makedirs(dir_detections, exist_ok=True)
os.makedirs(dir_clean_frames, exist_ok=True)

COOLDOWN_SECONDS = 3.0
_last_saved_at = 0.0
 
 
def save_debug_frame(results, original_frame):
    global _last_saved_at

    now = time.monotonic()
    if now - _last_saved_at < COOLDOWN_SECONDS:
        return
    _last_saved_at = now

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # e.g. 20260727_143012_512
    
    # for detections
    annotated = results[0].plot(img=original_frame)  # draws boxes/labels/conf onto a copy of original_frame
    path_detections = os.path.join(dir_detections, f"{ts}.jpg")
    cv2.imwrite(path_detections, annotated)
    # simple retention: keep only the newest MAX_SAVED_FRAMES files, delete the rest
    files_detections = sorted(
        (os.path.join(dir_detections, f) for f in os.listdir(dir_detections)),
        key=os.path.getmtime,
    )
    for old_file in files_detections[:-MAX_SAVED_FRAMES]:
        os.remove(old_file)

    # for clean frames
    path_clean_frames = os.path.join(dir_clean_frames, f"{ts}.jpg")
    cv2.imwrite(path_clean_frames, original_frame)
    # simple retention: keep only the newest MAX_SAVED_FRAMES files, delete the rest
    files_clean_frames = sorted(
        (os.path.join(dir_clean_frames, f) for f in os.listdir(dir_clean_frames)),
        key=os.path.getmtime,
    )
    for old_file in files_clean_frames[:-MAX_SAVED_FRAMES]:
        os.remove(old_file)

