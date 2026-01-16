import cv2  # Open Source Computer Vision Librart

# open camera
camera = cv2.VideoCapture(0)  # 0 means default camera (try 1,2,etc)
# check
if not camera.isOpened():
    print('Error: could not open the camera')
    exit()
print('Camera opened')

# loop continuously to read frames
while True:  # runs forever until q
    # get frame
    success, frame = camera.read()  # grab 1 frame (px grid img) + T/F
    # check
    if not success:
        print('Error: could not read frame')
        break
    # display the frame in a window
    cv2.imshow('Live Video', frame)  # prepare title + img to display (new frame each itteration)
    # show window (wait 1 ms for a key press. if user presses q, break loop and close)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing camera...")
        break

# release camera and close all windows
camera.release()  # so other programs can use it
cv2.destroyAllWindows()
print('Done')





