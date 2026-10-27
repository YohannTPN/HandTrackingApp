import cv2
import numpy as np

class Panel :
    def __init__(self, pos, size, sliders, color_wheel):
        self.pos = pos
        self.size = size
        self.sliders = sliders
        self.color_wheel = color_wheel

    def draw(self, view):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(view, (x, y), (x + w, y + h), (230, 230, 230), -1)
        cv2.rectangle(view, (x, y), (x + w, y + h), (100, 100, 100), 2)

        wx, wy = self.color_wheel.pos
        ww, wh = self.color_wheel.size
        view[wy:wy + wh, wx:wx + ww] = self.color_wheel.wheel_image
        color_wheel = view[wy:wy + wh, wx:wx + ww]
        color_wheel_mask = self.color_wheel.mask
        color_wheel[color_wheel_mask == 0] = (230, 230, 230)

        for slider in self.sliders:
            sx, sy = slider.pos
            sw, sh = slider.size
            cv2.rectangle(view, (sx, sy), (sx + sw, sy + sh), (200, 200, 200), -1)
            cv2.rectangle(view, (sx, sy), (sx + sw, sy + sh), (100, 100, 100), 2)
            hx, hy = slider.selected_value()
            cv2.circle(view, (hx, hy), 8, (50, 50, 50), -1)
            cv2.putText(view, f"{slider.get_brush_value()}", (sx + sw + 10, sy + sh // 2 + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
    def contains(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x <= px + w and py <= y <= py + h

    def slider_at(self, point):
        for slider in self.sliders:
            if slider.contains(point):
                return slider
        return None

    

    