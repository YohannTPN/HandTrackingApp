import math
from HandLandMarker import HandLandMarker
from Ui import UI

THUMB_TIP, INDEX_TIP = 4, 8
WRIST, MIDDLE_MCP = 0, 9


class HandPaint(HandLandMarker):
    """Paint contrôlé par le pincement pouce + index."""

    PINCH_ON = 0.20    # ratio en dessous duquel on commence à dessiner
    PINCH_OFF = 0.30   # ratio au dessus duquel on s'arrête 
    SMOOTHING = 0.5    # 1 = aucun lissage, plus bas = plus lisse mais plus lent

    def __init__(self, model_path, ui=None):
        super().__init__(model_path, num_hands=1)
        self.ui = ui or UI()
        self.pinching = False
        self.prev_point = None
        self.smooth_point = None
        self.cursor = None

        self.was_pinching = False
        self.is_clicking_button = False


    # ---------- Geste ----------

    @staticmethod
    def pinch_ratio(points):
        """Distance pouce-index divisée par la taille de la main.

        La division rend la mesure indépendante de la distance à la caméra.
        """
        hand_size = math.dist(points[WRIST], points[MIDDLE_MCP])
        if hand_size == 0:
            return 1.0
        return math.dist(points[THUMB_TIP], points[INDEX_TIP]) / hand_size

    def update_pinch_state(self, ratio):
        # Hystérésis : deux seuils différents évitent le clignotement
        if self.pinching:
            self.pinching = ratio < self.PINCH_OFF
        else:
            self.pinching = ratio < self.PINCH_ON

    # ---------- Point de dessin ----------

    def brush_position(self, points):
        """Milieu du pouce et de l'index : stable même quand les doigts se touchent."""
        tx, ty = points[THUMB_TIP]
        ix, iy = points[INDEX_TIP]
        raw = ((tx + ix) / 2, (ty + iy) / 2)

        if self.smooth_point is None:
            self.smooth_point = raw
        else:
            a = self.SMOOTHING
            self.smooth_point = (a * raw[0] + (1 - a) * self.smooth_point[0],
                                 a * raw[1] + (1 - a) * self.smooth_point[1])
        return int(self.smooth_point[0]), int(self.smooth_point[1])

    def release(self):
        """Coupe le trait en cours."""
        self.pinching = False
        self.prev_point = None
        self.smooth_point = None
        self.is_clicking_button = False

    # ---------- Hooks ----------

    def on_frame(self, frame, result):
        h, w = frame.shape[:2]
        self.ui.ensure_canvas(w, h)
        self.cursor = None

        if not result.hand_landmarks:
            self.release()
            return

        points = self.to_pixels(result.hand_landmarks[0], w, h)
        self.draw_hand(frame, points, self.get_label(result, 0))

        self.was_pinching = self.pinching

        self.update_pinch_state(self.pinch_ratio(points))

        start_pinching = self.pinching and not self.was_pinching


        self.cursor = self.brush_position(points)



        if start_pinching:
            self.is_clicking_button = self.ui.handle_click(self.cursor)
        
        if not self.pinching :
            self.is_clicking_button = False

        if self.pinching and not self.is_clicking_button:
            if self.prev_point is not None:
                self.ui.draw_line(self.prev_point, self.cursor)
            self.prev_point = self.cursor
        else:
            self.prev_point = None

    def render(self, frame):
        self.ui.show(frame, self.cursor, self.pinching)

    def on_key(self, key):
        if key == ord('s'):
            self.ui.save()
        return super().on_key(key)