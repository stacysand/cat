import sys  # for a clean non-zero exit so systemd can restart the program
 
from config import RTSP_URL
from shutdown import ShutdownHandler
from stream_reader import StreamReader
from stream_manager import StreamManager
from detection import detect_objects
from trigger_buzzer import trigger_buzzer_pi2_via_server
from save_frames import save_detections_and_cleanframe
 
 
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
 
        if frame is None:
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
