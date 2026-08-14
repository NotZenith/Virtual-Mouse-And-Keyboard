# Virtual Control Center

A high-performance virtual keyboard and mouse controller powered by MediaPipe and OpenCV. This project allows you to control your computer using only your hands through a standard webcam.

## Features

- **Smooth Virtual Mouse**: Right-hand control with exponential smoothing and acceleration.
- **Gesture Support**:
  - **Left Click / Drag**: Thumb + Middle finger pinch.
  - **Right Click**: Thumb + Index finger pinch.
  - **Scroll**: Thumb + Pinky pinch (move hand up/down).
- **Virtual Keyboard**: Modular keyboard with hover effects and animations.
- **Clap-to-Toggle**: Double clap to switch between Mouse and Keyboard modes.
- **Auto-Calibration**: Dynamically adjusts gesture thresholds based on your hand size.
- **Glassmorphism UI**: Modern dashboard with real-time FPS and status tracking.
- **Persistent Settings**: Configurations saved automatically in `settings.json`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NotZenith/Virtual-Mouse-And-Keyboard.git
   cd Virtual-Mouse-And-Keyboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Controls

- **Q**: Quit application.
- **R**: Restart calibration.
- **Tab**: Switch between available cameras.
- **Double Clap**: Toggle Keyboard Mode.

## Requirements

- Python 3.8+
- Webcam
- Requirements listed in `requirements.txt` (OpenCV, MediaPipe, cvzone, pynput, pyautogui)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
