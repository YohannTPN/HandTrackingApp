import cv2
import numpy as np

class ColorWheel:
    def __init__(self,pos,size, initial_color=(0, 0, 0)):
        self.pos = pos
        self.size = size
        self.color = initial_color
        self.wheel_image = self._create_color_wheel()

    def _create_color_wheel(self):
        hue = np.linspace(0, 1, self.size[0])
        saturation = np.linspace(0, 1, self.size[1])
        hue, saturation = np.meshgrid(hue, saturation)
        value = np.ones_like(hue) * 255
        hsv = np.stack([hue * 179, saturation * 255, value], axis=-1)
        bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return bgr

    def select_color(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        if px <= x < px + w and py <= y < py + h:
            relative_x = int((x - px) / w * self.wheel_image.shape[1])
            relative_y = int((y - py) / h * self.wheel_image.shape[0])
            self.color = tuple(int(c) for c in self.wheel_image[relative_y, relative_x])
            return self.color
        return None
