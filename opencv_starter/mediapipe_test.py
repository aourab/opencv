import cv2
import mediapipe as mp
import serial
import time

# Initialize sc
bluetooth = serial.Serial(port='COM3', baudrate=9600)
time.sleep(2)  

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

def send_command(command):
    """Send the specified command to Arduino."""
    bluetooth.write(command.encode())
    print(f"Command sent: {command}")
    time.sleep(1)

while True:
    ret, frame = cap.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hand landmarks
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Simple gesture recognition based on landmark positions
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # Example gesture logic (You can refine this based on your needs)
            if index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y:
                print("Gesture: Forward")
                send_command(commands['forward'])
            elif index_tip.y > thumb_tip.y and middle_tip.y > thumb_tip.y:
                print("Gesture: Backward")
                send_command(commands['backward'])
            elif index_tip.x < thumb_tip.x:
                print("Gesture: Left")
                send_command(commands['left'])
            elif index_tip.x > thumb_tip.x:
                print("Gesture: Right")
                send_command(commands['right'])
            else:
                print("Gesture: Stop")
                send_command(commands['stop'])
                
    cv2.imshow('MediaPipe Hands', frame)
    
    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
bluetooth.close()