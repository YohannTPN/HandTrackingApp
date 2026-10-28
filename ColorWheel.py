import cv2
import numpy as np

class ColorWheel:
    def __init__(self,pos,size, initial_color=(0, 0, 0),brightness=255):
        self.pos = pos
        self.size = size
        self.color = initial_color
        self.brightness = brightness
        self.mask = None
        self.wheel_image = self._create_color_wheel()

    def _update_wheel_image(self):
        self.wheel_image = self._create_color_wheel()

    def _create_color_wheel(self):
        x = np.linspace(0, self.size[0] - 1, self.size[0])
        y = np.linspace(0, self.size[1] - 1, self.size[1])
        x, y = np.meshgrid(x, y)
        center = (self.size[0] // 2, self.size[1] // 2)
        radius = self.size[0] // 2
        dx,dy = x - center[0], y - center[1]
        distance = np.hypot(dx, dy)
        theta = np.arctan2(dy, dx) + np.pi
        hue = theta / (2 * np.pi) * 179
        saturation = np.clip(distance / radius, 0, 1)
        value = np.ones_like(hue) * self.brightness
        hsv = np.stack([hue , saturation * 255, value], axis=-1)
        bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        self.mask = (distance <= radius).astype(np.uint8) * 255
        return bgr

    def select_color(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        if px <= x < px + w and py <= y < py + h:
            relative_x = int((x - px))
            relative_y = int((y - py))
            if self.mask[relative_y, relative_x] == 0:
                return None
            self.color = tuple(int(c) for c in self.wheel_image[relative_y, relative_x])
            return self.color
        return None
