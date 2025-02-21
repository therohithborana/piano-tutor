import cv2
import mediapipe as mp
import pygame
import numpy as np
import time

pygame.mixer.init()

# Add song sequences
SONGS = {
    'Happy Birthday': ['C', 'C', 'D', 'C', 'F', 'E',
                      'C', 'C', 'D', 'C', 'G', 'F',
                      'C', 'C', 'C1', 'A', 'F', 'E', 'D']
}

# Add marker positions for each note
NOTE_POSITIONS = {
    'C': (100, 200),   # Left hand - index finger
    'D': (150, 200),   # Left hand - middle finger
    'E': (200, 200),   # Left hand - ring finger
    'F': (250, 200),   # Left hand - pinky
    'G': (400, 200),   # Right hand - pinky
    'A': (450, 200),   # Right hand - ring finger
    'B': (500, 200),   # Right hand - middle finger
    'C1': (550, 200)   # Right hand - index finger
}

notes = {
    'C': pygame.mixer.Sound("C.wav"),
    'D': pygame.mixer.Sound("D.wav"),
    'E': pygame.mixer.Sound("E.wav"),
    'F': pygame.mixer.Sound("F.wav"),
    'G': pygame.mixer.Sound("G.wav"),
    'A': pygame.mixer.Sound("A.wav"),
    'B': pygame.mixer.Sound("B.wav"),
    'C1': pygame.mixer.Sound("C1.wav")
}

# Add tutorial state
class TutorialState:
    def __init__(self):
        self.current_song = 'Happy Birthday'
        self.current_note_index = 0
        self.last_played_time = 0
        self.note_played = False

tutorial = TutorialState()

def draw_markers(image):
    # Draw the current note marker
    current_note = SONGS[tutorial.current_song][tutorial.current_note_index]
    x, y = NOTE_POSITIONS[current_note]
    cv2.circle(image, (x, y), 20, (0, 255, 0), 2)
    cv2.putText(image, current_note, (x-10, y+5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Draw all notes and their positions
    cv2.putText(image, "Finger Guide:", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Left hand notes
    cv2.putText(image, "Right Hand:", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(image, "Index (C)", (10, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Middle (D)", (10, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Ring (E)", (10, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Pinky (F)", (10, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Right hand notes
    cv2.putText(image, "Left Hand:", (10, 170), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(image, "Pinky (G)", (10, 190), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Ring (A)", (10, 210), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Middle (B)", (10, 230), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(image, "Index (C1)", (10, 250), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def check_note_played(hand_landmarks, hand_index, note):
    if hand_index == 0:  # Left hand
        if note == 'C' and hand_landmarks.landmark[8].y > hand_landmarks.landmark[7].y:
            return True
        elif note == 'D' and hand_landmarks.landmark[12].y > hand_landmarks.landmark[11].y:
            return True
        elif note == 'E' and hand_landmarks.landmark[16].y > hand_landmarks.landmark[15].y:
            return True
        elif note == 'F' and hand_landmarks.landmark[20].y > hand_landmarks.landmark[19].y:
            return True
    elif hand_index == 1:  # Right hand
        if note == 'G' and hand_landmarks.landmark[20].y > hand_landmarks.landmark[19].y:
            return True
        elif note == 'A' and hand_landmarks.landmark[16].y > hand_landmarks.landmark[15].y:
            return True
        elif note == 'B' and hand_landmarks.landmark[12].y > hand_landmarks.landmark[11].y:
            return True
        elif note == 'C1' and hand_landmarks.landmark[8].y > hand_landmarks.landmark[7].y:
            return True
    return False

def update_tutorial(hand_landmarks, hand_index):
    current_note = SONGS[tutorial.current_song][tutorial.current_note_index]
    wrong_note_played = False
    
    # Check if any note is being played
    for note in notes:
        if check_note_played(hand_landmarks, hand_index, note) and note != current_note:
            wrong_note_played = True
            break
    
    if wrong_note_played:
        # Show red indicator
        x, y = NOTE_POSITIONS[current_note]
        cv2.circle(image, (x, y), 25, (0, 0, 255), 2)
        cv2.putText(image, "Wrong Note!", (x-40, y-30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif check_note_played(hand_landmarks, hand_index, current_note):
        if not tutorial.note_played:
            notes[current_note].play()
            tutorial.note_played = True
            tutorial.last_played_time = time.time()
    else:
        if tutorial.note_played and (time.time() - tutorial.last_played_time > 0.5):
            tutorial.current_note_index = (tutorial.current_note_index + 1) % len(SONGS[tutorial.current_song])
            tutorial.note_played = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands = 2)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            update_tutorial(hand_landmarks, i)

    draw_markers(image)
    cv2.imshow('Hand Gesture Music Player', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()