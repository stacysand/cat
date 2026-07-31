import os
import cv2
from datetime import datetime
import time

from config import COOLDOWN_SECONDS, MAX_SAVED_FRAMES, DIR_DETECTIONS, DIR_CLEAN_FRAMES


# paths
os.makedirs(DIR_DETECTIONS, exist_ok=True)
os.makedirs(DIR_CLEAN_FRAMES, exist_ok=True)

# timing
last_saved_at = 0.0
 
def save_detections_and_cleanframe(frame_original, frame_roi, results):
    
    # timing
    global last_saved_at
    now = time.monotonic()
    if now - last_saved_at < COOLDOWN_SECONDS:
        return  # still in cooldown, skip
    last_saved_at = now

    # file names
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # e.g. 20260727_143012_512
    
    # detections
    frame_annotated = results[0].plot(img=frame_roi)  # draws boxes/labels/conf onto a copy of original_frame
    path_detections = os.path.join(DIR_DETECTIONS, f"{ts}.jpg")
    cv2.imwrite(path_detections, frame_annotated)
    # simple retention: keep only the newest MAX_SAVED_FRAMES files, delete the rest
    files_detections = sorted(
        (os.path.join(DIR_DETECTIONS, f) for f in os.listdir(DIR_DETECTIONS)),
        key=os.path.getmtime,
    )
    for old_file in files_detections[:-MAX_SAVED_FRAMES]:
        os.remove(old_file)

    # clean frames
    path_clean_frames = os.path.join(DIR_CLEAN_FRAMES, f"{ts}.jpg")
    cv2.imwrite(path_clean_frames, frame_original)
    # simple retention: keep only the newest MAX_SAVED_FRAMES files, delete the rest
    files_clean_frames = sorted(
        (os.path.join(DIR_CLEAN_FRAMES, f) for f in os.listdir(DIR_CLEAN_FRAMES)),
        key=os.path.getmtime,
    )
    for old_file in files_clean_frames[:-MAX_SAVED_FRAMES]:
        os.remove(old_file)

