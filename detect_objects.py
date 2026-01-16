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

# loop continuously to read frames
while True:  # runs forever until q
    # get frame
    success, frame = camera.read()  # grab 1 frame (px grid img) + T/F
    if not success:
        print('Error: could not read frame')
        break
    
    # run model on the frame
    results = model(frame)
    annotated_frame = results[0].plot()  # draw detection boxes and labels on the frame

    # display the frame in a window
    cv2.imshow('YOLOv8 Detection', annotated_frame)  # prepare title + img to display (new frame each itteration)
    # show window (wait 1 ms for a key press. if user presses q, break loop and close)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing...")
        break

# release camera and close all windows
camera.release()  # so other programs can use it
cv2.destroyAllWindows()
print('Done')


