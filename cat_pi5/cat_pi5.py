import sys  # for a clean non-zero exit so systemd can restart the program
import time  # for sleep timer

from config import RTSP_URL, IDLE_POLL_INTERVAL
from shutdown import ShutdownHandler
from stream_reader import StreamReader
from stream_manager import StreamManager
from detection import detect_objects
from trigger_buzzer import trigger_buzzer_pi2_via_server
from save_positives import save_detections_and_cleanframe
from motion_check import find_px_diff_between_frames
 
 
def main():
    shutdown = ShutdownHandler()
 
    stream_reader = StreamReader(RTSP_URL).start()
    try:
        stream_manager = StreamManager(stream_reader)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
 
    print('Streaming')
 
    while not shutdown.requested:
        try:
            frame = stream_manager.get_frame()
        except RuntimeError as e:
            print(f"[main] {e}, exiting so systemd restarts us")
            sys.exit(1)
 
        # check for usable frame
        if frame is None:
            time.sleep(IDLE_POLL_INTERVAL)
            continue

        # check for motion (px diff found >> activate YOLO)
        if not find_px_diff_between_frames(frame):  # stop if (not True) = False:
            time.sleep(IDLE_POLL_INTERVAL)
            continue

        # run detection
        frame_original, frame_roi, results, target = detect_objects(frame)

        # trigger functions
        if target:
            save_detections_and_cleanframe(frame_original, frame_roi, results)
            trigger_buzzer_pi2_via_server()
 
    stream_manager.stop()
    print("Done")
 
 
if __name__ == "__main__":
    main()
