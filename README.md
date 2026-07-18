# Fall Detection

## Overview

This project presents a fall detection system based on computer vision and MediaPipe Pose. It analyzes human body posture from recorded video input by estimating body orientation using the body aspect ratio and torso angle. When a fall is confirmed for a predefined period, the system automatically captures a screenshot, plays an alarm sound, and sends a Telegram notification.

## Demo



https://github.com/user-attachments/assets/6d314d7f-3680-46a9-96c5-96de7324af63

## Telegram Alert

<img width="578" height="94" alt="Screenshot 2026-07-15 164745" src="https://github.com/user-attachments/assets/74ae10dc-d67a-4825-bb0f-4d54620f0cd8" />



## Features

- Human pose estimation using MediaPipe Pose
- Fall detection based on body aspect ratio and torso angle
- Temporal validation to reduce false detections
- Automatic alarm activation
- Telegram notification
- Automatic screenshot capture
- Video processing and output generation

## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Pygame
- Requests
- Tkinter

## Installation

```bash
git clone https://github.com/yourusername/Fall-Detection.git
cd Fall-Detection
pip install -r requirements.txt
```

## Usage

```bash
python falldetection.py
```

1. Select the input video.
2. Select the alarm sound.
3. The system analyzes the video.
4. If a fall is confirmed, an alarm is triggered, a screenshot is saved, and a Telegram notification is sent.
5. The processed video is saved automatically.

## Detection Process

1. Read the input video.
2. Estimate the human pose using MediaPipe Pose.
3. Calculate the body aspect ratio and torso angle.
4. Detect potential falls using predefined thresholds.
5. Confirm the fall over multiple consecutive frames.
6. Trigger the alert system.
7. Save the processed output video.

## Applications

- Elderly monitoring
- Smart healthcare
- Home surveillance
- Assisted living systems

## Future Improvements

- Real-time camera support
- Multi-person fall detection
- Activity recognition
- Cloud-based notification services
- Mobile application integration

## Author

Nourhan Ahmed
