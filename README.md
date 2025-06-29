# GestureControl
GestureControl is a Python-based desktop tool that allows users to control their mouse and trigger system actions using only hand gestures detected via a webcam. Built with OpenCV, MediaPipe, PyAutoGUI, and system tray integration, GestureControl brings a touchless and accessible interface to your fingertips quite literally. 



## 🚀 Features

* 🖱️ Control the mouse cursor with index finger movements.
* 👆 Perform left click, right click, and double click via predefined hand gestures.
* 📸 Capture screenshots with a specific hand gesture.
* 📦 Works in the background with system tray icon and keyboard hotkey support.
* 🧠 Uses MediaPipe hand tracking for robust real-time detection.
* 🛠️ Easy to run and cross-platform compatible.

## 🧰 Technologies Used

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* PyStray
* Pynput
* PIL (Pillow)
* Keyboard

## 💻 How to Use

1. Clone the repository and navigate into the project folder:

   ```bash
   git clone https://github.com/yourusername/GestureControl.git
   cd GestureControl
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python gesture_control.py
   ```

4. Press `Ctrl + H` to toggle gesture control on or off.

5. Use your hand in front of the webcam to control the mouse or trigger actions.

## 📝 Notes

* Ensure your camera is connected and accessible.
* Designed for use with one hand (right-hand optimized).
* The `hand_landmark_tracking_cpu.binarypb` model file is auto-copied if not already present.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

Feel free to fork, contribute, and improve HawkEye for broader gesture support and accessibility tools!
