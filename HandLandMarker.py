import mediapipe as mp
from mediapipe.tasks.python import vision
import cv2
import time

model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # pouce
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # majeur
    (9, 13), (13, 14), (14, 15), (15, 16),   # annulaire
    (13, 17), (17, 18), (18, 19), (19, 20),  # auriculaire
    (0, 17),                                 # bord de la paume
]

SWAP_HANDEDNESS = {"Left": "Right", "Right": "Left"}

class HandLandMarker:

    def __init__(self, model_path):
        self.model_path = model_path

        self.base_options = BaseOptions(model_asset_path=self.model_path)
        self.options = HandLandmarkerOptions(
            base_options=self.base_options,
            num_hands=2,
            running_mode=VisionRunningMode.VIDEO
        )
        self.detector = HandLandmarker.create_from_options(self.options)

    def annotate_frame(self, frame, result):
        h, w = frame.shape[:2]

        for idx, hand in enumerate(result.hand_landmarks):
            keypoints = [(int(lm.x * w), int(lm.y * h)) for lm in hand]

            label = result.handedness[idx][0].category_name
            label = SWAP_HANDEDNESS[label]  # correction de l'inversion

            # Traits
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, keypoints[a], keypoints[b], (255, 255, 255), 2)

            # Points
            for (x, y) in keypoints:
                cv2.circle(frame, (x, y), 5, (255, 200, 50), -1)

            # Étiquette près du poignet
            wx, wy = keypoints[0]
            cv2.putText(frame, label, (wx - 20, wy + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


    def process_webcam(self):
        cap = cv2.VideoCapture(0)
        start = time.time()
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)


            timestamp_ms = int((time.time() - start) * 1000)
            result = self.detector.detect_for_video(mp_image, timestamp_ms)

            self.annotate_frame(frame, result)

            cv2.imshow('MediaPipe Hand Landmarker', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()




        









