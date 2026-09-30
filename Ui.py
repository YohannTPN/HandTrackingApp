import time
import cv2
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class UI:
    """Gère le canvas et l'affichage (fenêtres Camera et Paint).

    Ne connaît rien de MediaPipe : elle reçoit juste des points en pixels.
    """

    def __init__(self, color=BLACK, thickness=6):
        self.color = color
        self.thickness = thickness
        self.canvas = None

    # ---------- Canvas ----------

    def ensure_canvas(self, w, h):
        if self.canvas is None:
            self.canvas = np.full((h, w, 3), 255, dtype=np.uint8)

    def draw_line(self, p1, p2):
        cv2.line(self.canvas, p1, p2, self.color, self.thickness, cv2.LINE_AA)

    def save(self):
        filename = f"paint_{int(time.time())}.png"
        cv2.imwrite(filename, self.canvas)
        print(f"Dessin sauvegardé : {filename}")

    # ---------- Affichage ----------

    def show(self, camera_frame, cursor=None, drawing=False):
        cv2.imshow('Camera', camera_frame)
        cv2.imshow('Paint', self._compose(cursor, drawing))

    def _compose(self, cursor, drawing):
        view = self.canvas.copy()

        if cursor is not None:
            radius = max(self.thickness, 6)
            # Plein = en train de dessiner, contour = curseur seul
            cv2.circle(view, cursor, radius, (0, 0, 255), -1 if drawing else 2)

        status = "Dessin" if drawing else "Pause (pince pouce + index pour dessiner)"
        cv2.putText(view, status, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1)
        cv2.putText(view, "s: sauver | q: quitter", (10, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
        return view