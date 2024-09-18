import cv2
import mediapipe as mp
import serial
import time

# Initialize Bluetooth connection (uncomment and adjust the port if using Bluetooth)
# bluetooth = serial.Serial(port='COM3', baudrate=9600)
# time.sleep(2)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize drawing utilities
mp_draw = mp.solutions.drawing_utils

# Define command mapping based on gestures
commands = {
    'forward': 'F',
    'backward': 'B',
    'left': 'L',
    'right': 'R',
    'stop': 'S',
    'fold': 'M1',
    'unfold': 'M2',
    'toggle_control': 'TOGGLE'
}

# Gesture control variables
control_on = False  # Initially control is off
last_command = None  # Keep track of the last command
closed_fist_threshold = 0.2  # Threshold for recognizing a closed fist

# Load an image (static)
img = cv2.imread("photos/feed_cv.jpg")

def send_command(command):
    """Send the specified command to Arduino."""
    # Uncomment the line below to actually send the command to the Arduino via Bluetooth
    # bluetooth.write((command + '\n').encode())
    print(f"Command sent: {command}")
    time.sleep(0.5)  # Delay to avoid sending too many commands too quickly

# Convert the image to RGB
rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Detect hand landmarks
result = hands.process(rgb_frame)

if result.multi_hand_landmarks:
    for hand_landmarks in result.multi_hand_landmarks:
        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Get relevant landmarks for gesture recognition
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

        # Calculate distances for closed fist detection
        thumb_index_dist = abs(thumb_tip.y - index_tip.y)
        thumb_middle_dist = abs(thumb_tip.y - middle_tip.y)
        thumb_ring_dist = abs(thumb_tip.y - ring_tip.y)
        thumb_pinky_dist = abs(thumb_tip.y - pinky_tip.y)

        command = "Stop"  # Default command

        # Closed fist (all fingers are close together) means "Stop"
        if (thumb_index_dist < closed_fist_threshold and
            thumb_middle_dist < closed_fist_threshold and
            thumb_ring_dist < closed_fist_threshold and
            thumb_pinky_dist < closed_fist_threshold):
            command = "Stop"

        # Toggle gesture (open hand: index and middle fingers extended, thumb down)
        elif index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y:
            command = "Forward"

        # Backward gesture (both fingers below the thumb)
        elif index_tip.y > thumb_tip.y and middle_tip.y > thumb_tip.y:
            command = "Backward"

        # Left gesture (index finger on the left side of thumb)
        elif index_tip.x < thumb_tip.x:
            command = "Left"

        # Right gesture (index finger on the right side of thumb)
        elif index_tip.x > thumb_tip.x:
            command = "Right"

        # Gesture for folding/unfolding (ring and pinky fingers involved)
        elif ring_tip.y < wrist.y and pinky_tip.y < wrist.y:
            if control_on:
                command = "Fold" if not last_command == "Fold" else "Unfold"

        # Draw bounding box around hand
        x_min = min([lm.x for lm in hand_landmarks.landmark])
        y_min = min([lm.y for lm in hand_landmarks.landmark])
        x_max = max([lm.x for lm in hand_landmarks.landmark])
        y_max = max([lm.y for lm in hand_landmarks.landmark])

        # Convert normalized coordinates to pixel values
        x_min = int(x_min * img.shape[1])
        y_min = int(y_min * img.shape[0])
        x_max = int(x_max * img.shape[1])
        y_max = int(y_max * img.shape[0])

        # Draw rectangle around the detected hand
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        # Draw the detected command on the screen near the hand
        cv2.putText(img, command, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Send the command only if control is enabled
        if control_on and command != last_command:
            if command == "Fold" or command == "Unfold":
                send_command(commands[command.lower()])  # Send folding/unfolding commands
            else:
                send_command(commands[command.lower()])
            last_command = command

# Display the processed image
cv2.imshow('Image', img)

# Press any key to close the window
cv2.waitKey(0)
cv2.destroyAllWindows()
# bluetooth.close()  # Close Bluetooth connection when program exits
