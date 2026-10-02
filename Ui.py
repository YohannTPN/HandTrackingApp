import time
import cv2
import numpy as np

from Button import Button

DEFAULT_THICKNESS = 6
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class UI:
    """Gère le canvas et l'affichage (fenêtres Camera et Paint).

    Ne connaît rien de MediaPipe : elle reçoit juste des points en pixels.
    """

    def __init__(self, color=BLACK, thickness=DEFAULT_THICKNESS, buttons=None):
        self.color = color
        self.thickness = thickness
        self.canvas = None
        self.buttons = buttons if buttons is not None else []

        self.add_button((10, 10), (100, 30), "Rouge", lambda: self.change_color((0, 0, 255)))
        self.add_button((120, 10), (100, 30), "Vert", lambda: self.change_color((0, 255, 0)))
        self.add_button((230, 10), (100, 30), "Bleu", lambda: self.change_color((255, 0, 0)))
        self.add_button((340, 10), (100, 30), "Black", lambda: self.change_color((0, 0, 0)))
        self.add_button((450, 10), (100, 30), "Gomme", lambda: self.use_eraser())

    # ---------- Canvas ----------

    def change_color(self, color):
        self.thickness = DEFAULT_THICKNESS
        self.color = color

    def use_eraser(self):
        self.color = WHITE
        self.thickness = 20

    def ensure_canvas(self, w, h):
        if self.canvas is None:
            self.canvas = np.full((h, w, 3), 255, dtype=np.uint8)

    def draw_line(self, p1, p2):
        cv2.line(self.canvas, p1, p2, self.color, self.thickness, cv2.LINE_AA)

    def add_button(self, pos, size, label, action):
        self.buttons.append(Button(pos, size, label, action))

    def button_at(self, point):
        for button in self.buttons:
            if button.contains(point):
                return button
        return None

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

        

        for button in self.buttons:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(view, (x, y), (x + w, y + h), (200, 200, 200), -1)
            cv2.rectangle(view, (x, y), (x + w, y + h), (100, 100, 100), 2)
            cv2.putText(view, button.label, (x + 10, y + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 1)

        if cursor is not None:
            radius = max(self.thickness, 6)
            # Plein = en train de dessiner, contour = curseur seul
            cv2.circle(view, cursor, radius, (0, 0, 255), -1 if drawing else 2)
            button = self.button_at(cursor)
            if button is not None:
                x, y = button.pos
                w, h = button.size
                cv2.rectangle(view, (x, y), (x + w, y + h), (0, 0, 255), 2)


            

        status = "Dessin" if drawing else "Pause (pince pouce + index pour dessiner)"
        cv2.putText(view, status, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1)
        cv2.putText(view, "s: sauver | q: quitter", (10, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
        return view