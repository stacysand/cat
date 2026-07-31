import signal  # to handle shutdown signals from systemd or Ctrl+C
 
 
class ShutdownHandler:
    # answers one question: has a stop been requested 
    def __init__(self):
        self.requested = False
        signal.signal(signal.SIGTERM, self._handle)  # sent by systemd on service stop
        signal.signal(signal.SIGINT, self._handle)   # sent by Ctrl+C
 
    def _handle(self, sig, frame):
        self.requested = True
