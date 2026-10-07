import time
import cv2
import numpy as np
from collections import deque

from Button import Button
from ColorWheel import ColorWheel
from Brush import Brush

DEFAULT_THICKNESS = 6
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)


class UI:
    """Gère le canvas et l'affichage (fenêtres Camera et Paint).

    Ne connaît rien de MediaPipe : elle reçoit juste des points en pixels.
    """

    def __init__(self, brush=None, buttons=None, color_wheel=None):
        
        self.brush = brush if brush is not None else Brush()
        self.eraser = Brush(color=WHITE, thickness=20)
        
        self.canvas = None
        self.buttons = buttons if buttons is not None else []
        self.is_color_wheel_open = False
        self.color_wheel = color_wheel if color_wheel is not None else ColorWheel((10, 50), (200, 200))

        self.active_tool = "brush"  # "brush" ou "eraser" ou "fill"

        self.actions_history = deque(maxlen=10)  # Historique des actions pour l'annulation
        self.restore_history = deque(maxlen=10)  # Historique des actions pour la restauration après annulation


        self.add_button((10, 10), (110, 30), "Color Wheel", lambda: self.open_color_wheel())
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
        self.brush.thickness = DEFAULT_THICKNESS
        self.active_tool = "brush"
        self.brush.color = color

    def open_color_wheel(self):
        self.is_color_wheel_open = True

    def use_brush(self):
        self.active_tool = "brush"
        self.brush.thickness = DEFAULT_THICKNESS
        self.brush.color = self.brush.color if self.brush.color != WHITE else BLACK

    def use_eraser(self):
        self.active_tool = "eraser"
        self.brush.color = self.eraser.color
        self.brush.thickness = self.eraser.thickness

    def use_fill(self):
        self.active_tool = "fill"
        self.brush.color = self.brush.color if self.brush.color != WHITE else BLACK
        self.brush.thickness = DEFAULT_THICKNESS

    def fill_canvas(self, canvas, point):
        """Remplit le canvas à partir d'un point donné."""
        h, w = canvas.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(canvas, mask, point, self.brush.color, flags=cv2.FLOODFILL_FIXED_RANGE,loDiff=(30, 30, 30), upDiff=(30, 30, 30))





    def ensure_canvas(self, w, h):
        if self.canvas is None:
            self.canvas = np.full((h, w, 3), 255, dtype=np.uint8)

    def draw_line(self, p1, p2):
        cv2.line(self.canvas, p1, p2, self.brush.color, self.brush.thickness, cv2.LINE_8)

    def add_button(self, pos, size, label, action):
        self.buttons.append(Button(pos, size, label, action))

    def button_at(self, point):
        for button in self.buttons:
            if button.contains(point):
                return button
        return None

    def handle_click(self, point):
        button = self.button_at(point)
        if self.is_color_wheel_open:
            if self.color_wheel.select_color(point) is not None:
                self.change_color(self.color_wheel.color)
                return True
            else :
                self.is_color_wheel_open = False
                return True

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

        if self.is_color_wheel_open:
            x, y = self.color_wheel.pos
            w, h = self.color_wheel.size
            wheel_image = self.color_wheel.wheel_image
            view[y:y + h, x:x + w] = wheel_image

        if cursor is not None:
            if self.active_tool == "eraser":
                radius = max(self.brush.thickness, 10)
                cv2.circle(view, cursor, radius//2, GREY, 2)
            else:
                radius = max(self.brush.thickness, 6)
                # Plein = en train de dessiner, contour = curseur seul
                cv2.circle(view, cursor, radius, self.brush.color, -1 if drawing else 2)


            button = self.button_at(cursor)
            if button is not None:
                x, y = button.pos
                w, h = button.size
                cv2.rectangle(view, (x, y), (x + w, y + h), (0, 0, 255), 2)


            

        status = "Dessin" if drawing else "Pause (pince pouce + index pour dessiner)"
        cv2.putText(view, status, (260, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 90, 90), 1)
        cv2.putText(view, "s: sauver | q: quitter", (10, view.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
        return view