import cv2
import mediapipe as mp
import numpy as np
import os
import datetime
import pygame
from tkinter import Tk, filedialog
import requests


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# =========================
#        FALL DETECTOR
# =========================
class FallDetector:

    def __init__(self, ratio_threshold=0.8, angle_threshold=45,
                 fall_frames_threshold=5):

        self.ratio_threshold = ratio_threshold
        self.angle_threshold = angle_threshold
        self.fall_frames_threshold = fall_frames_threshold
        self.fall_counter = 0

    def detect(self, landmarks, frame_w, frame_h):

        xs = [lm.x * frame_w for lm in landmarks]
        ys = [lm.y * frame_h for lm in landmarks]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        width = x_max - x_min
        height = y_max - y_min

        if height < 1e-6:
            return False, 0, 0

        ratio = width / height

        ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        shoulder_mid = ((ls.x + rs.x) / 2 * frame_w,
                        (ls.y + rs.y) / 2 * frame_h)

        hip_mid = ((lh.x + rh.x) / 2 * frame_w,
                   (lh.y + rh.y) / 2 * frame_h)

        dx = hip_mid[0] - shoulder_mid[0]
        dy = hip_mid[1] - shoulder_mid[1]
        angle = np.degrees(np.arctan2(abs(dx), abs(dy) + 1e-6))

        is_fall = ratio > self.ratio_threshold and angle > self.angle_threshold

        if is_fall:
            self.fall_counter += 1
        else:
            self.fall_counter = max(0, self.fall_counter - 1)

        return self.fall_counter >= self.fall_frames_threshold, ratio, angle


# =========================
#        ALERT SYSTEM
# =========================
class AlertManager:

    def __init__(self,
                 sound_file=None,
                 enable_sound=True,
                 enable_telegram=True,
                 bot_token="",
                 chat_id=""):

        self.sound_file = sound_file
        self.enable_sound = enable_sound

        self.enable_telegram = enable_telegram
        self.bot_token = bot_token
        self.chat_id = chat_id

        self.last_alert_time = None

        os.makedirs("fall_screenshots", exist_ok=True)
        pygame.mixer.init()

        os.makedirs("fall_screenshots", exist_ok=True)
        pygame.mixer.init()

    # -------- SOUND --------
    def _play_sound(self):
        if not self.enable_sound or not self.sound_file:
            return
        try:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            print("Sound Error:", e)

    # -------- TELEGRAM --------
    def _send_telegram(self):

        if not self.enable_telegram:
            return

        try:

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            data = {
                "chat_id": self.chat_id,
                "text": "⚠ FALL DETECTED! Someone may need help."
            }

            requests.post(url, data=data)

            print("Telegram Alert Sent!")

        except Exception as e:
            print("Telegram Error:", e)

    # -------- SCREENSHOT --------
    def _save(self, frame):
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"fall_screenshots/fall_{name}.jpg"
        cv2.imwrite(path, frame)
        return path

    # -------- TRIGGER --------
    def trigger(self, frame):

        now = datetime.datetime.now()

        if self.last_alert_time:
            if (now - self.last_alert_time).seconds < 10:
                return

        self.last_alert_time = now

        self._save(frame)
        self._play_sound()
        self._send_telegram()

        print(f"[ALERT] Fall detected at {now}")


# =========================
#     MAIN FUNCTION
# =========================
def run_fall_detection(video_path, alert):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Cannot open video")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        "output.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )
    detector = FallDetector(
        fall_frames_threshold=int(fps * 5)
    )

    fall_start_time = None
    ALERT_DELAY = 5 # 5 seconds

    with mp_pose.Pose(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as pose:

        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                fallen, ratio, angle = detector.detect(
                    results.pose_landmarks.landmark,
                    width,
                    height
                )

                if fallen:

                    cv2.putText(frame, "FALL DETECTED!",
                                (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 3)

                    cv2.rectangle(frame, (0, 0),
                                  (width, height),
                                  (0, 0, 255), 3)

                    # Start timer when fall begins
                    if fall_start_time is None:
                        fall_start_time = datetime.datetime.now()

                    elapsed = (
                            datetime.datetime.now() -
                            fall_start_time
                    ).total_seconds()

                    cv2.putText(
                        frame,
                        f"On Ground: {elapsed:.1f}s",
                        (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

                    # Alert after 5 seconds
                    if elapsed >= ALERT_DELAY:

                        cv2.putText(
                            frame,
                            "EMERGENCY!",
                            (10, 170),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            3
                        )

                        if not was_fallen:
                            alert.trigger(frame)

                        was_fallen = True

                else:

                    fall_start_time = None
                    was_fallen = False

            out.write(frame)
            cv2.imshow("Fall Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Saved video output.mp4")


# =========================
#          RUN
# =========================
if __name__ == "__main__":

    root = Tk()
    root.withdraw()

    video_path = filedialog.askopenfilename(
        title="Select Video"
    )

    sound_file = filedialog.askopenfilename(
        title="Select Sound"
    )

    alert = AlertManager(
        sound_file=sound_file,
        enable_sound=True,
        enable_telegram=True,
        bot_token="8951743804:AAE_KSQpFcg4ngr3x4Wwrvar2EQzmEeIRYM",
        chat_id="1062322947"
    )

    run_fall_detection(video_path, alert)