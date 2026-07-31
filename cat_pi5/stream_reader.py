import cv2
import threading  # Python standard library for separate threads
 
 
# -------------------------------------  Reader Thread  ------------------------------------------------------
 
class StreamReader:  # continuously reads frames in a background thread, holds only the latest frame
 
    def __init__(self, url):  # url = "rtsp://..." (passed in by the caller, e.g. from config.py)
        # remember the url so a caller (StreamManager) can reconnect without needing to know it separately:
        self.url = url
        # connect to camera:
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)  # create a video capture object; use the FFmpeg backend (better than OpenCV's default one)
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
        # create a daemon thread so it runs "_read_loop.
        self._thread = threading.Thread(target=self._read_loop, daemon=True)  # daemon=True - thread will automatically die when main program exits
        # start daemon thread:
        self._thread.start()  # after this line, 2 things run at the same time: main thread and background thread running "_read_loop"
        return self  # just pattern to write object and method in one line (like "StreamReader().start()")
 
    # infinite loop that keeps reading frames
    def _read_loop(self):
        while self.running:
            # wrap cap.read() in try/except:
            # If FFmpeg has a decode error (e.g., like "bytestream -5" in logs) instead of returning ok=False,
            # mark the thread as stopped instead of the exception silently killing the thread
            try:
                ok, frame = self.cap.read()  # return (success_flag, frame) - in numpy array format (R,G,B)
            except Exception as e:
                print(f"[StreamReader] read() raised an exception: {e}")
                ok, frame = False, None
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
        # shutdown thread:
        self._thread.join()
        # release the video:
        self.cap.release()
