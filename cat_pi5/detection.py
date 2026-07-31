import cv2
from ultralytics import YOLO

from config import MODEL_NAME, ROI, TARGET_CLASSES

model = YOLO(MODEL_NAME)

def detect_objects(frame):
    
    frame_original = frame.copy()

    # prepare frame with roi
    frame_roi = frame.copy()
    frame_roi = cv2.fillPoly(frame_roi, [ROI], 0)  # draw roi (pollygon)
    
    # get model detections
    results = model(frame_roi)

    # check for target
    detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]  # get detected classes as a list
    target = any(c in TARGET_CLASSES for c in detected_classes)  # exact classes we want
    
    return frame_original, frame_roi, results, target 
