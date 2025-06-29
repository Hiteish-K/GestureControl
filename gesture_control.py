import cv2
import mediapipe as mp
import pyautogui
import keyboard
import threading
from pynput.mouse import Button, Controller
from pystray import Icon, MenuItem, Menu
from PIL import Image
import time
import datetime
import numpy as np
import os
import sys
import shutil

# Set the correct path for Mediapipe hand landmark model

def get_resource_path(relative_path):
    """Get the correct path for resources when running as an EXE."""
    if getattr(sys, 'frozen', False):  # Check if running as PyInstaller EXE
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Correct path to Mediapipe model
source_file = get_resource_path("mediapipe/modules/hand_landmark/hand_landmark_tracking_cpu.binarypb")
dest_folder = os.path.join(os.getcwd(), "mediapipe", "modules", "hand_landmark")
os.makedirs(dest_folder, exist_ok=True)

# Destination file path
dest_file = os.path.join(dest_folder, "hand_landmark_tracking_cpu.binarypb")

# Copy the file if necessary
if not os.path.exists(dest_file):
    shutil.copy(source_file, dest_file)

# Mouse Controller
mouse = Controller()
screen_width, screen_height = pyautogui.size()

# MediaPipe Hand Detection Setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

# Gesture Control Status
gesture_control_active = False
running = True  # Used to stop threads safely

# Utility Functions
def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    return np.abs(np.degrees(radians))

def get_distance(landmark_list):
    if len(landmark_list) < 2:
        return 0  # Prevents crashes
    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
    return np.hypot(x2 - x1, y2 - y1) * 1000  # Scaled properly

# Toggle Gesture Control
def toggle_gesture_control():
    global gesture_control_active
    gesture_control_active = not gesture_control_active
    print("Gesture Control:", "Enabled" if gesture_control_active else "Disabled")

# Find Index Finger Tip
def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        return processed.multi_hand_landmarks[0].landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return None

# Move Mouse Smoothly
def move_mouse(index_finger_tip):
    if index_finger_tip and gesture_control_active:
        x, y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y / 2 * screen_height)
        pyautogui.moveTo(x, y, duration=0.05)

# Gesture Recognition Functions
def is_left_click(landmark_list, thumb_index_dist):
    return get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90 and thumb_index_dist > 50

def is_right_click(landmark_list, thumb_index_dist):
    return get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and thumb_index_dist > 50

def is_double_click(landmark_list, thumb_index_dist):
    return get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and thumb_index_dist > 50

def is_screenshot(landmark_list, thumb_index_dist):
    return get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and thumb_index_dist < 50

# Detect Gestures & Perform Actions
def detect_gesture(frame, landmark_list, processed):
    if not gesture_control_active or len(landmark_list) < 21:
        return

    index_finger_tip = find_finger_tip(processed)
    thumb_index_dist = get_distance([landmark_list[4], landmark_list[5]])

    if thumb_index_dist < 50 and get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
        move_mouse(index_finger_tip)
    elif is_left_click(landmark_list, thumb_index_dist):
        mouse.press(Button.left)
        mouse.release(Button.left)
        cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    elif is_right_click(landmark_list, thumb_index_dist):
        mouse.press(Button.right)
        mouse.release(Button.right)
        cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    elif is_double_click(landmark_list, thumb_index_dist):
        pyautogui.doubleClick()
        cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    elif is_screenshot(landmark_list, thumb_index_dist):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pyautogui.screenshot().save(f'screenshot_{timestamp}.png')
        cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

# Main Gesture Control Function
def gesture_control():
    global running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    draw = mp.solutions.drawing_utils

    while running:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed = hands.process(frameRGB)

        landmark_list = []
        if processed.multi_hand_landmarks:
            hand_landmarks = processed.multi_hand_landmarks[0]
            draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
            for lm in hand_landmarks.landmark:
                landmark_list.append((lm.x, lm.y))

        detect_gesture(frame, landmark_list, processed)

        if gesture_control_active:
            cv2.imshow('Gesture Control', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Exit Application
def exit_app(icon, item):
    global running
    running = False
    icon.stop()
    sys.exit()

# System Tray Icon
def run_tray():
    image = Image.new('RGB', (64, 64), (255, 0, 0))
    menu = Menu(MenuItem('Toggle Gesture Control', toggle_gesture_control), MenuItem('Exit', exit_app))
    icon = Icon('gesture_control', image, menu=menu)
    icon.run()

# Run Script
if __name__ == "__main__":
    keyboard.add_hotkey("ctrl+h", toggle_gesture_control)

    gesture_thread = threading.Thread(target=gesture_control)
    gesture_thread.daemon = True
    gesture_thread.start()

    run_tray()
