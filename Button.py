class Button :
    def __init__(self,pos,size,label,action):
        self.pos = pos
        self.size = size
        self.label = label
        self.action = action

    def contains(self, point):
        x,y = point
        px,py = self.pos
        w,h = self.size
        return px <= x <= px + w and py <= y <= py + h

    