import cv2  # Open Source Computer Vision Librart
from ultralytics import YOLO

# load model
model = YOLO('yolov8n.pt')  # Nano is the smallest v. Alternatives yolov8m.pt, yolov8l.pt

# open camera
camera = cv2.VideoCapture(0)  # 0 means default camera (try 1,2,etc)
if not camera.isOpened():
    print('Error: could not open the camera')
    exit()
print('Camera opened')

# ROI coordinates
roi_table = (1100, 400, 1900, 700)  # Region Of Interest

# loop continuously to read frames
while True:  # runs forever until q
    # get frame
    success, frame = camera.read()  # grab 1 frame (px grid img) + T/F
    if not success:
        print('Error: could not read frame')
        break
    
    # create copy to draw on
    frame_detect = frame.copy()
    
    # process table roi
    x1_t, y1_t, x2_t, y2_t = roi_table
    # crop the region
    crop_table = frame[y1_t:y2_t, x1_t:x2_t]  # OpenCV order: ver cut (from one row to another), hor cut (from one column to another)
    # run model on table_crop
    results_table = model(crop_table)
    annotated_table = results_table[0].plot()  # draw detection boxes and labels on the frame

    # Place annotated crop back onto full frame at the same location
    frame_detect[y1_t:y2_t, x1_t:x2_t] = annotated_table

    # draw the table roi
    cv2.rectangle(frame_detect, (x1_t, y1_t), (x2_t, y2_t), (255,0,0), 2)  # top-left & bottom-right corners; (B,G,R); thickness=2
    # add roi label
    # cv2.putText(frame, 'Table', (roi_table[0], roi_table[1] - 10),
    #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # display the frame in a window
    cv2.imshow('ROI Detection', frame_detect)  # prepare title + img to display (new frame each itteration)
    # show window (wait 1 ms for a key press. if user presses q, break loop and close)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing...")
        break

# release camera and close all windows
camera.release()  # so other programs can use it
cv2.destroyAllWindows()
print('Done')
