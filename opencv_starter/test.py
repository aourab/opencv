import cv2
import mediapipe as mp
import requests
import time

# ESP8266 IP and Port (replace with your NodeMCU's IP address)
ESP8266_IP = "http://192.168.10.78"  # Replace with your ESP8266's IP address

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

# Open video capture (webcam)
cap = cv2.VideoCapture(0)

# Ensure video capture is working
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

def send_command(command):
    """Send the specified command to the ESP8266 over HTTP."""
    url = f"{ESP8266_IP}/{command}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Command '{command}' sent successfully")
        else:
            print(f"Failed to send command '{command}'")
    except Exception as e:
        print(f"Error sending command: {e}")

while True:
    ret, frame = cap.read()
    
    # Ensure the frame is valid
    if not ret:
        print("Failed to capture image.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hand landmarks
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

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

            command = "stop"  # Default command

            # Closed fist (all fingers are close together) means "Stop"
            if (thumb_index_dist < closed_fist_threshold and
                thumb_middle_dist < closed_fist_threshold and
                thumb_ring_dist < closed_fist_threshold and
                thumb_pinky_dist < closed_fist_threshold):
                command = "stop"

            # Toggle control gesture (open hand with thumb down)
            elif index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y:
                if not control_on:  # If control is off, turn it on
                    command = "toggle_control"
                    control_on = True
                else:
                    command = "forward"

            # Backward gesture (both fingers below the thumb)
            elif index_tip.y > thumb_tip.y and middle_tip.y > thumb_tip.y:
                command = "backward"

            # Left gesture (index finger on the left side of thumb)
            elif index_tip.x < thumb_tip.x:
                command = "left"

            # Right gesture (index finger on the right side of thumb)
            elif index_tip.x > thumb_tip.x:
                command = "right"

            # Gesture for folding/unfolding (ring and pinky fingers raised)
            elif ring_tip.y < wrist.y and pinky_tip.y < wrist.y:
                command = "fold" if not last_command == "fold" else "unfold"

            if control_on:
                if command != last_command:
                    send_command(commands[command.lower()])  # Use .lower() to match dictionary keys
                    last_command = command

            # Draw the command on the frame
            cv2.putText(frame, command.capitalize(), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Hand Gesture Control', frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
