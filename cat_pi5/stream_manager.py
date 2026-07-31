import time  # to measure how long the frame has been stuck
 
from stream_reader import StreamReader
from config import STALE_TIMEOUT, MAX_RECONNECTS
 
 
# -------------------------------------  Stream Health / Self-Healing  -----------------------------------------
 
class StreamManager:
    """Wraps a StreamReader with staleness detection and reconnect logic.
    Answers one question: 'is my video connection healthy and current —
    and if not, fix it.' StreamReader handles the low-level reading;
    this class notices when that reading has silently gone bad and
    replaces the reader when it has.
 
    Takes an already-started StreamReader rather than constructing one
    itself, so main.py can see both entities explicitly instead of one
    hiding inside the other."""
 
    def __init__(self, stream_reader, stale_timeout=STALE_TIMEOUT, max_reconnects=MAX_RECONNECTS):
        self.stream = stream_reader
        if not self.stream.cap.isOpened():
            raise RuntimeError("Could not open the stream")
 
        self.stale_timeout = stale_timeout
        self.max_reconnects = max_reconnects
 
        # bookkeeping used to detect a stuck stream
        self.last_frame_bytes = None          # the last frame actually processed
        self.last_change_time = time.time()   # when the picture last actually changed
        self.reconnect_attempts = 0           # consecutive failed reconnect attempts
 
    def _reconnect(self):
        """Tear down the current RTSP connection and open a brand new one from scratch."""
        print("[StreamManager] Stream looks stuck — reconnecting...")
        self.stream.stop()
        new_stream = StreamReader(self.stream.url).start()
        if not new_stream.cap.isOpened():
            return False
        self.stream = new_stream
        return True
 
    def _handle_reconnect(self):
        ok = self._reconnect()
        self.reconnect_attempts = 0 if ok else self.reconnect_attempts + 1
        if self.reconnect_attempts >= self.max_reconnects:
            raise RuntimeError("Too many failed reconnects")
        self.last_frame_bytes = None
        self.last_change_time = time.time()
 
    def get_frame(self):
        """Returns a fresh frame, or None if none is available right now
        (e.g. right after a reconnect). Reconnects automatically if the
        reader thread died or the picture has been stuck too long.
        Raises RuntimeError once reconnects are exhausted — the caller
        should exit so systemd restarts the process."""
        # if the reader thread already noticed a real failure (ok=False):
        # reconnect immediately instead of waiting for the staleness timer below
        if not self.stream.running:
            self._handle_reconnect()
            return None
 
        frame = self.stream.get_frame()
        if frame is None:
            return None
 
        # compare the raw bytes of the frame to the last one processed.
        # this checks that the stream isn't stuck
        frame_bytes = frame.tobytes()
        if frame_bytes == self.last_frame_bytes:
            if time.time() - self.last_change_time > self.stale_timeout:
                self._handle_reconnect()
                return None  # just reconnected, caller should grab a brand new frame next loop
        else:
            self.last_frame_bytes = frame_bytes
            self.last_change_time = time.time()
 
        return frame
 
    def stop(self):
        self.stream.stop()
