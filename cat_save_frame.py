import cv2  # Open Source Computer Vision Library (OpenCV) - for working with video, images, display
import threading  # Python standard library for separate threads
from ultralytics import YOLO  # CV model
from actions import trigger_function
from save_frame import save_debug_frame
import numpy as np
import requests  # for Flask on Pi >> buzzer

# -------------------------------------  Reader Thread  ------------------------------------------------------

class StreamReader:  # continuously reads frames in a background thread, holds only the latest frame
    
    def __init__(self, url):  # url = "rtsp://..." (defined below)
        # connect to camera:
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)  # create a video capture object; use the FFmpeg backend (better than OpenCV’s default one)
        # only 1 frame in internal buffer:
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # set - change property of video capture; CAP_PROP_BUFFERSIZE = size of the OpenCV internal buffer; =1
        # shared variable between two threads:
        self.frame = None  # initially, there is no frame yet. but reader thread will write new frames here
        # lock:
        self.lock = threading.Lock()  # (also called Mutex (mutual exclusion))
        # flag to control the reading loop
        self.running = False  # initially set to False → reader thread should NOT run yet. when we call start(), this will change to True

    # create a daemon thread
    def start(self):
        # set running flag to True:
        self.running = True  # flag is used later in the background thread to know whether it should keep reading frames or stop
        # create a daemon thread so it runs ""_read_loop.
        self._thread = threading.Thread(target=self._read_loop, daemon=True)  # daemon=Trus - thread will automatically die when main program exits
        # start daemon thread:
        self._thread.start()  # after this line, 2 things run at the same time: main thread and background thread running "_read_loop"
        return self  # just pattern to write object and method in one line (like "StreamReader().start()")

    # infinite loop that keeps reading frames
    def _read_loop(self):
        while self.running:
            # get success_flag and frame:
            ok, frame = self.cap.read()  # return (success_flag, frame) - in numpy array format (R,G,B)
            # if success_flag is failed:
            if not ok:
                # set running flag to False:
                self.running = False
                # stop:
                break
            # acquire lock:
            with self.lock:
                # get the frame:
                self.frame = frame

    # get copy of the frame
    def get_frame(self):
        # acquire lock:
        with self.lock:
            # copy the frame
            return self.frame.copy() if self.frame is not None else None

    # stop the thread reader
    def stop(self):
        # set running flag to False:
        self.running = False
        # shutdowm threads:
        self._thread.join()
        # release the video:
        self.cap.release()


# -------------------------------------------  Main Thread  --------------------------------------------------------------

# load model
model = YOLO('yolov8n.pt')  # Nano is the smallest v. Alternatives yolov8m.pt, yolov8l.pt

# ROI coordinates
roi_table = np.array([
    [500, 380],
    [810, 400],
    [750, 710],
    [150, 710],
], dtype=np.int32)  # top-left, top-right, bottom-right, bottom-left

# stream
stream = StreamReader("rtsp://192.168.1.173:8554/cam").start()  # # connect to the network stream
if not stream.cap.isOpened():
    print('Error: could not open the stream')
    exit()
print('Streaming')

# loop continuously to read frames
while True:  # runs forever until q
    frame = stream.get_frame()
    if frame is None: 
        continue

    # create copy to draw on
    frame_detect = frame.copy()

    # process table roi
    x1_t, y1_t, x2_t, y2_t = roi_table

    # mask roi and run detection on full frame
    masked = frame.copy()
    cv2.fillPoly(masked, [roi_table], 0)
    results = model(masked)

    # check for cat or dog
    detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls]
    # if any(c in ('cat', 'dog') for c in detected_classes):
    if any(c in ('person') for c in detected_classes):  # for check only
        trigger_function()
        save_debug_frame(results, frame_detect)

    # draw detection boxes and labels on the frame
    frame_detect = results[0].plot()

    # draw the table roi
    cv2.polylines(frame_detect, [roi_table], isClosed=True, color=(255, 0, 0), thickness=2)  # top-left & bottom-right corners; (B,G,R); thickness=2
    # add roi label
    # cv2.putText(frame, 'Table', (roi_table[0], roi_table[1] - 10),
    #           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # display the frame in a window
    cv2.imshow('ROI Detection', frame_detect)  # prepare title + img to display (new frame each itteration)

    # show window (wait 1 ms for a key press. if user presses q, break loop and close)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing...")
        break

stream.stop()
cv2.destroyAllWindows()
print("Done")
