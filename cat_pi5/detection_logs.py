import json
import os
from datetime import datetime
 
from config import DIR_DETECTION_LOGS
from detection import model  # reuse the already-loaded model for class-name lookup
 
 
os.makedirs(DIR_DETECTION_LOGS, exist_ok=True)
LOG_PATH = os.path.join(DIR_DETECTION_LOGS, "detections_log.jsonl")
 
 
def results_to_detections(results):
    # convert YOLO results object into a list of plain dicts [{"class": "cat", "conf": 0.83, "box": [x1, y1, x2, y2]}, ...]
    detections = []
    boxes = results[0].boxes
    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i])
        detections.append({
            "class": model.names[cls_id],
            "conf": round(float(boxes.conf[i]), 4),
            "box": [round(v, 1) for v in boxes.xyxy[i].tolist()],
        })
    return detections
 
 
def log_event(event_type, image_path, detections):
    """
    Append one line to the shared jsonl log describing a saved frame.
    event_type: "detection" | "raw_periodic" | "raw_post_sighting" | "raw_post_person_exit"
 
    One log file across every save source (trigger-based and raw-sampled)
    so later triage can sort/filter the whole collection at once - e.g.
    with pandas or FiftyOne - instead of opening images one by one.
    """
    record = {
        "ts": datetime.now().isoformat(timespec="milliseconds"),
        "event_type": event_type,
        "image": image_path,
        "detections": detections,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
