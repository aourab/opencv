import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize drawing utilities
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Define command mapping based on gestures
commands = {
    'forward': 'F',
    'backward': 'B',
    'left': 'L',
    'right': 'R',
        'stop': 'S',
    'fold': 'M1',
    'unfold': 'M2'
}

# Initialize hand control toggle
control_on = False

def fingers_are_closed(hand_landmarks, w, h):
    """Check if all fingers are closed (based on relative distances between tips and base)."""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

    # Check if each finger tip is close to the MCP (finger base)
    return (thumb_tip.y > thumb_mcp.y and index_tip.y > index_mcp.y and
            middle_tip.y > middle_mcp.y and ring_tip.y > ring_mcp.y and pinky_tip.y > pinky_mcp.y)

while True:
    ret, frame = cap.read()
    
    # Flip the frame horizontally for a mirror view
    frame = cv2.flip(frame, 1)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hand landmarks
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Find the bounding box for the hand
            h, w, c = frame.shape
            x_min, y_min = w, h
            x_max, y_max = 0, 0
            
            for landmark in hand_landmarks.landmark:
                x, y = int(landmark.x * w), int(landmark.y * h)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            
            # Draw a rectangle around the hand
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            # Gesture recognition
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            command = "Stop"  # Default command
            
            # Toggle control on/off with thumbs-up gesture
            if index_tip.y < thumb_tip.y and not control_on:
                control_on = True
                print("Hand Control: ON")
            elif index_tip.y > thumb_tip.y and control_on:
                control_on = False
                print("Hand Control: OFF")
            
            if control_on:
                # Recognize closed fingers for "Stop"
                if fingers_are_closed(hand_landmarks, w, h):
                    command = "Stop"
                
                # Recognize other gestures only if fingers are open
                elif index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y:
                    command = "Forward"
                elif index_tip.y > thumb_tip.y and middle_tip.y > thumb_tip.y:
                    command = "Backward"
                elif index_tip.x < thumb_tip.x:
                    command = "Left"
                elif index_tip.x > thumb_tip.x:
                    command = "Right"
                elif index_tip.y < middle_tip.y:  # Example gesture for fold
                    command = "Fold"
                elif index_tip.y > middle_tip.y:  # Example gesture for unfold
                    command = "Unfold"
            
            # Display the command on the corner of the rectangle
            cv2.putText(frame, command, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('MediaPipe Hands with Commands (Flipped)', frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
