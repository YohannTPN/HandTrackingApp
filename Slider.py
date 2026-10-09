class Slider :
    def __init__(self, pos, size, min_val, max_val,get_brush_value, set_brush_value,step=1):
        self.pos = pos
        self.size = size
        self.min_val = min_val
        self.max_val = max_val
        self.get_brush_value = get_brush_value
        self.set_brush_value = set_brush_value
        self.step = step



    def contains(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x <= px + w and py <= y <= py + h

    def set_value_from_point(self, point):
        x = point[0]
        px = self.pos[0]
        w = self.size[0]   
        relative_x = x - px
        value = self.min_val + (relative_x / w) * (self.max_val - self.min_val)
        value = max(self.min_val, min(self.max_val, value))
        value = round(value / self.step) * self.step
        self.set_brush_value(value)

    def selected_value(self):
        px, py = self.pos
        w, h = self.size
        relative_x = (self.get_brush_value() - self.min_val) / (self.max_val - self.min_val) * w
        relative_x = max(0, min(w, relative_x))
        return int(px + relative_x), int(py + h // 2)