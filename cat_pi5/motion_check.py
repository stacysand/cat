import time
import cv2

from config import ROI, BLUR_KERNEL, DIFF_THRESHOLD, MIN_CHANGED_PXS, IDLE_TIMEOUT


frame_last = None  # previous prepared frame
last_change_time = time.monotonic()  # # last time real motion was seen
yolo_status = True  # start assuming activity until proven quiet

# prepare frame for comparing
def prepare_frame(frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # make grayscale frame
    frame_gray_roi = cv2.fillPoly(frame_gray, [ROI], 0)  # use same roi as for detection
    frame_gray_roi_blur = cv2.GaussianBlur(frame_gray_roi, BLUR_KERNEL, 0)  # add blur
    return frame_gray_roi_blur

# main function
def find_px_diff_between_frames(frame):
    
    global frame_last, last_change_time, yolo_status
    
    # get gray,roi,blurred frame
    frame_current = prepare_frame(frame)

    # compute difference between current and previous frames
    if frame_last is not None:
        # compute pixel difference
        px_difference = cv2.absdiff(frame_last, frame_current)
        # compute threshold to consider difference is significant
        _, thresholded = cv2.threshold(px_difference, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
        # apply threshold and find how many pixels survived
        changed_pxs = cv2.countNonZero(thresholded)
        # find how many of survived pixels count as real motion, not noise
        if changed_pxs >= MIN_CHANGED_PXS:  # if above the noise threshold:
            last_change_time = time.monotonic()  # start time
            yolo_status = True  # activate YOLO
    
    frame_last = frame_current
    
    # stop YOLO if diff is not found for some time:
    if yolo_status and time.monotonic() - last_change_time > IDLE_TIMEOUT:
        yolo_status = False

    return yolo_status
