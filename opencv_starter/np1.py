import numpy as np
import cv2

background = None
hand = None

frames_elapsed = 0
FRAME_HEIGHT = 600
FRAME_WIDTH = 900

CALIBRATION_TIME = 30
BG_WEIGHT = 0.5 
OBJ_THRESHOLD = 18 

capture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame = cv2.flip(frame, 1)

    cv2.imshow("cam input", frame)

    if cv2.waitKey(1) & 0xFF == ord("x"):
        break

capture.release()
cv2.destroyAllWindows()  # Fixed typo here

# our region of interest

region_top = 0
region_bottom = int(2 * FRAME_HEIGHT / 3)
region_left = int(FRAME_WIDTH / 2)
region_right = FRAME_WIDTH

frames_elapsed = 0

class HandData:
    def __init__(self, top, bottom, left, right, centerX):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.centerX = centerX
        self.prevCenterX = 0
        self.isInFrame = False
        self.isWaving = False
        self.fingers = 0

    def update(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    # writing on screen
    @staticmethod
    def write_on_image(frame, hand):
        global frames_elapsed  # Use global to access frames_elapsed

        text = "searching"

        if frames_elapsed < CALIBRATION_TIME:
            text = "calibrating..."
        elif hand is None or hand.isInFrame is False:  # Fixed attribute typo here
            text = "No hands in frame"
        else: 
            if hand.isWaving:
                text = "waving"
            elif hand.fingers == 0:
                text = "Rock"
            elif hand.fingers == 1:
                text = "pointing"
            elif hand.fingers == 2:
                text = "scissors"

        # Display text on the frame
        cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        # Highlight the region of interest using a drawn rectangle.
        cv2.rectangle(frame, (region_left, region_top), (region_right, region_bottom), (255, 255, 255), 2)

# Example of calling the method
# Make sure to pass the correct frame and hand data when calling write_on_image
# HandData.write_on_image(frame, hand)
