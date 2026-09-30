import time
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision

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
    """Détection de mains sur webcam.

    Points d'extension pour les classes filles :
      - on_frame(frame, result) : traitement à chaque image
      - render(frame)           : affichage
      - on_key(key)             : gestion clavier (retourne False pour quitter)
    """

    def __init__(self, model_path, num_hands=2, camera_index=0):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_hands=num_hands,
            running_mode=VisionRunningMode.VIDEO,
        )
        self.detector = HandLandmarker.create_from_options(options)
        self.camera_index = camera_index
        self._start = None
        self._last_ts = -1

    # ---------- Détection ----------

    def detect(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        ts = int((time.time() - self._start) * 1000)
        ts = max(ts, self._last_ts + 1)  
        self._last_ts = ts
        return self.detector.detect_for_video(mp_image, ts)

    # ---------- Utilitaires ----------

    @staticmethod
    def to_pixels(hand, w, h):
        """Landmarks normalisés (0-1) -> liste de points (x, y) en pixels."""
        return [(int(lm.x * w), int(lm.y * h)) for lm in hand]

    @staticmethod
    def get_label(result, idx):
        """'Left' / 'Right' corrigé (l'image est en miroir)."""
        return SWAP_HANDEDNESS[result.handedness[idx][0].category_name]

    @staticmethod
    def draw_hand(frame, points, label=None):
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, points[a], points[b], (255, 255, 255), 2)
        for p in points:
            cv2.circle(frame, p, 5, (255, 200, 50), -1)
        if label:
            wx, wy = points[0]
            cv2.putText(frame, label, (wx - 20, wy + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    

    # ---------- Hooks (à surcharger) ----------

    def on_frame(self, frame, result):
        """Comportement par défaut : dessiner toutes les mains détectées."""
        h, w = frame.shape[:2]
        for idx, hand in enumerate(result.hand_landmarks):
            self.draw_hand(frame, self.to_pixels(hand, w, h),
                           self.get_label(result, idx))

    def render(self, frame):
        cv2.imshow('Hand Landmarker', frame)

    def on_key(self, key):
        return key != ord('q')

    # ---------- Boucle principale ----------

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        self._start = time.time()
        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                frame = cv2.flip(frame, 1)
                result = self.detect(frame)

                self.on_frame(frame, result)
                self.render(frame)

                if not self.on_key(cv2.waitKey(1) & 0xFF):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()