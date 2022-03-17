import pygame as pg

class Rect(pg.Rect):
    def __init__(self, pos, left, top, width, height):
        self.pos = pos
        super().__init__(left, top,width, height)

class Playfield:
    def __init__(self,rectDims,size,playfieldSize,res):
        self.rectDims = rectDims
        self.size = size
        self.rectSize = self.calculateRectSizes()
        self.sidePaddingPx = res[0] * round((1-playfieldSize[0])/2, 3)
        self.topPaddingPx = res[1] * round((1-playfieldSize[1])/2, 3)
        self.rects = self.createRects()
    def calculateRectSizes(self):
        width = self.size[0] / self.rectDims[0]
        height = self.size[1] / self.rectDims[1]
        return (width, height)
    def createRects(self):
        (cols, rows) = (self.rectDims[0], self.rectDims[1])
        rects = [[0 for x in range(rows)] for y in range(cols)]
        for col in range(0, cols):
            for row in range(0, rows):
                rect = Rect((col,row),self.sidePaddingPx+(col*self.rectSize[0]),self.topPaddingPx+(row*self.rectSize[1]),self.rectSize[0], self.rectSize[1])
                rects[col][row] = rect
        return rects

    