import time
import cv2
import numpy as np
from collections import deque

from Button import Button
from Slider import Slider
from ColorWheel import ColorWheel
from Brush import Brush
from Panel import Panel

DEFAULT_THICKNESS = 6
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

PANEL_MARGIN = 20
PANEL_GAP = 20
WHEEL_SIZE = 200
SLIDER_WIDTH = 160    # plus étroit que la roue : place pour afficher la valeur à droite
SLIDER_HEIGHT = 30


class UI:
    """Gère le canvas et l'affichage (fenêtres Camera et Paint).

    Ne connaît rien de MediaPipe : elle reçoit juste des points en pixels.
    """

    def __init__(self, brush=None, buttons=None):
        
        self.brush = brush if brush is not None else Brush()
        self.eraser = Brush(color=WHITE, thickness=20)
        
        self.canvas = None
        self.buttons = buttons if buttons is not None else []

        self.is_panel_open = False
        self.panel = None
        self.color_wheel = None

        self.active_tool = "brush"  # "brush" ou "eraser" ou "fill"
        self.active_slider = None

        self.actions_history = deque(maxlen=10)  # Historique des actions pour l'annulation
        self.restore_history = deque(maxlen=10)  # Historique des actions pour la restauration après annulation


        self.add_button((10, 10), (110, 30), "Panel", lambda: self.open_panel())
        self.add_button((140, 10), (80, 30), "Rouge", lambda: self.change_color((0, 0, 255)))
        self.add_button((240, 10), (80, 30), "Vert", lambda: self.change_color((0, 255, 0)))
        self.add_button((340, 10), (80, 30), "Bleu", lambda: self.change_color((255, 0, 0)))
        self.add_button((440, 10), (80, 30), "Black", lambda: self.change_color((0, 0, 0)))
        self.add_button((10, 40), (80, 30), "Brush", lambda: self.use_brush())
        self.add_button((140, 40), (80, 30), "Fill", lambda: self.use_fill())
        self.add_button((240, 40), (80, 30), "Gomme", lambda: self.use_eraser())
        self.add_button((340, 40), (80, 30), "Undo", lambda: self.pop_last_action())
        self.add_button((440, 40), (80, 30), "Restore", lambda: self.restore_state())

        

    # ---------- Canvas ----------
    

    def change_color(self, color):
        self.active_tool = "brush"
        self.brush.color = color

    def open_panel(self):
        self.is_panel_open = True

    def use_brush(self):
        self.active_tool = "brush"


    def use_eraser(self):
        self.active_tool = "eraser"


    def current_brush(self):
        if self.active_tool == "brush":
            return self.brush
        elif self.active_tool == "eraser":
            return self.eraser
        elif self.active_tool == "fill":
            return self.brush  

    def use_fill(self):
        self.active_tool = "fill"


    def fill_canvas(self, canvas, point):
        """Remplit le canvas à partir d'un point donné."""
        h, w = canvas.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(canvas, mask, point, self.current_brush().color, flags=cv2.FLOODFILL_FIXED_RANGE,loDiff=(30, 30, 30), upDiff=(30, 30, 30))





    def ensure_canvas(self, w, h):
        if self.canvas is None:
            self.canvas = np.full((h, w, 3), 255, dtype=np.uint8)
            self.build_panel(w, h)

    def draw_line(self, p1, p2):
        cv2.line(self.canvas, p1, p2, self.current_brush().color, self.current_brush().thickness, cv2.LINE_8)

    def add_button(self, pos, size, label, action):
        self.buttons.append(Button(pos, size, label, action))


    def button_at(self, point):
        for button in self.buttons:
            if button.contains(point):
                return button
        return None


    def on_drag(self, point):
        if self.active_slider is not None:
            self.active_slider.set_value_from_point(point)

    def on_release(self):
        if self.active_slider is not None:
            self.active_slider = None

    def handle_click(self, point):
        if self.is_panel_open:
            color = self.color_wheel.select_color(point)
            if color is not None:
                self.change_color(color)
                return True

            slider = self.panel.slider_at(point)
            if slider is not None:
                self.active_slider = slider
                slider.set_value_from_point(point)
                return True

            if not self.panel.contains(point):
                self.is_panel_open = False
            return True

        button = self.button_at(point)
        if button is not None:
            button.action()
            return True

        if self.active_tool == "fill":
            self.register_state()
            self.fill_canvas(self.canvas, point)
            return True

        return False

    def register_state(self):
        """Enregistre l'état actuel du canvas pour permettre l'annulation."""
        self.actions_history.append(self.canvas.copy())
        self.restore_history.clear()  

    def restore_state(self):
        """Restaure l'état précédent du canvas après une annulation."""
        if self.restore_history:
            last_state = self.restore_history.pop()
            self.actions_history.append(self.canvas.copy())
            self.canvas[:] = last_state[:]

    def pop_last_action(self):
        """Annule la dernière action."""
        if self.actions_history:
            self.restore_history.append(self.canvas.copy())  
            last_action = self.actions_history.pop()
            self.canvas[:] = last_action[:]

    # ---------- Brush Thickness ----------

    def get_brush_thickness(self):
        return self.current_brush().thickness

    def set_brush_thickness(self, thickness):
        self.current_brush().thickness = thickness
            


        

    def save(self):
        filename = f"paint_{int(time.time())}.png"
        cv2.imwrite(filename, self.canvas)
        print(f"Dessin sauvegardé : {filename}")

    # ---------- Affichage ----------

    def build_panel(self, frame_w, frame_h):
        """Calcule la disposition et crée le panneau centré dans l'image."""
        panel_w = PANEL_MARGIN * 2 + WHEEL_SIZE
        panel_h = PANEL_MARGIN * 2 + WHEEL_SIZE + PANEL_GAP + SLIDER_HEIGHT

        # Origine du panneau : centré dans l'image
        px = (frame_w - panel_w) // 2
        py = (frame_h - panel_h) // 2

        # Positions absolues des éléments
        wheel_pos = (px + PANEL_MARGIN, py + PANEL_MARGIN)
        slider_pos = (px + PANEL_MARGIN, wheel_pos[1] + WHEEL_SIZE + PANEL_GAP)

        self.color_wheel = ColorWheel(wheel_pos, (WHEEL_SIZE, WHEEL_SIZE))
        thickness_slider = Slider(slider_pos, (SLIDER_WIDTH, SLIDER_HEIGHT), 1, 50,
                                self.get_brush_thickness, self.set_brush_thickness, step=1)
        self.panel = Panel((px, py), (panel_w, panel_h), [thickness_slider], self.color_wheel)

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


        if self.is_panel_open:
            self.panel.draw(view)

        if cursor is not None:
            if self.active_tool == "eraser":
                radius = self.current_brush().thickness // 2
                cv2.circle(view, cursor, radius, GREY, 2)
            else:
                radius = max(self.current_brush().thickness, 3) // 2
                # Plein = en train de dessiner, contour = curseur seul
                cv2.circle(view, cursor, radius, self.current_brush().color, -1 if drawing else 2)


            button = self.button_at(cursor)
            if button is not None and not self.is_panel_open:
                x, y = button.pos
                w, h = button.size
                cv2.rectangle(view, (x, y), (x + w, y + h), (0, 0, 255), 2)


            

        status = "Dessin" if drawing else "Pause (pince pouce + index pour dessiner)"
        cv2.putText(view, status, (260, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1)
        cv2.putText(view, "s: sauver | q: quitter", (10, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
        return view