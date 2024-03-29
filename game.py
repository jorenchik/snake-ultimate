import pygame as pg
import time as t
import random as rd
import pickle as pc
import string
import ctypes
import collections
from pathlib import Path
from typing import List
from settings import *
from assets import *

# keys -> angle
pl1Keys = [pg.K_RIGHT,pg.K_UP,pg.K_LEFT,pg.K_DOWN]
pl2Keys = [pg.K_d,pg.K_w,pg.K_a,pg.K_s]
degrees = [0,90,180,270]

# Helper funtions
def dd(var):
    """
    Prints the variable and dies.
    """
    print(var)
    exit()

def get_key(val, dict):
    """
    Gets the key of the given value in the dictionary.
    """
    for key, value in dict.items():
         if val == value:
             return key

def pilImageToSurface(img):
    new_image = img.getdata()
    flat_list = [e for c in new_image for e in c]
    bute_array = (ctypes.c_ubyte * len(flat_list))(*flat_list)
    surf = pg.image.frombuffer(bute_array, img.size, img.mode).convert_alpha()
    return surf

class Rect(pg.Rect):
    """
    Represents a rectangle that has particular position on the playfield.
    """
    def __init__(self, pos:tuple, left:int, top:int, width:int, height:int):
        self.pos = pos
        super().__init__(left, top,width, height)

class Playfield:
    """
    Consists of rectangles that makes the playfield itself.
    """
    def __init__(self,rectDims:tuple,size:tuple,playfieldSize:tuple):
        self.rectDims = rectDims
        self.size = size
        self.sidePaddingPx = res[0] * round((1-playfieldSize[0])/2, 3)
        self.topPaddingPx = res[1] * round((1-playfieldSize[1])/2, 3)
        self.calculateRectSizes().createRects()
    def calculateRectSizes(self):
        """
        Calculates the width and height of a single rectangle with the given size and dimensions of the playfield.
        """
        self.rectSize = (self.size[0] / self.rectDims[0], self.size[1] / self.rectDims[1])
        return self
    def createRects(self):
        """
        Fills the playfield with rects according to its dimensions.
        """
        (cols, rows) = (self.rectDims[0], self.rectDims[1])
        rects = [[0 for x in range(rows)] for y in range(cols)]
        for col in range(0, cols):
            for row in range(0, rows):
                rect = Rect((col,row),self.sidePaddingPx+(col*self.rectSize[0]),self.topPaddingPx+(row*self.rectSize[1]),self.rectSize[0], self.rectSize[1])
                rects[col][row] = rect
        self.rects = rects
        return self


class Food():
    def __init__(self, isPoisonous:bool=False):
        """
        Represents a food entity that occupies one rectangle of the playfield.
        It can be of the type 'food' meaning that it adds one point and one part to a snake once gets hit hit or of the type 'poisonous' meaning it removes one point and one part of a snake once gets hit either.
        """
        # Position
        pos = game.getRandomAvailablePos()
        self.type = 'food' if not isPoisonous else 'poison'
        if pos: self.pos = (pos[0],pos[1])
        else:
            game.gameWon = True
            self.pos = (rd.randint(1,rectDims[0]-1),rd.randint(1,rectDims[1]-1))
        self.x, self.y = game.getCoords(self.pos)[0], game.getCoords(self.pos)[1]
        # Type
        self.poisonous = isPoisonous
        # Appearance
        self.rect = pg.Rect(self.x,self.y,game.playfield.rectSize[0],game.playfield.rectSize[1])
        img = pilImageToSurface(foodColoredImgs[self.type])
        self.sprite = pg.transform.scale(img,(playfield.rectSize[0]*1.02, playfield.rectSize[1]*1.02))
        self.color = foodColor


class SnakePart():
    """
    Represents a part of a snake that can be either alive or not.
    The class has two types - the 'head' and the 'body'.
    """
    def __init__(self,type:string,snakeIndex:int,color:tuple,pos:tuple=False,velocity:pg.Vector2=False):
        # General fields
        self.type, self.snakeIndex = type, snakeIndex
        self.getRelatedSnakeParts()
        # Physical fields
        randomPos = game.getRandomAvailablePos((1,playfield.rectDims[1]))
        self.pos = (pos[0] if pos else randomPos[0],pos[1] if pos else randomPos[1])
        self.prevPos, self.prevVelocity = pos, velocity
        self.x, self.y = game.getCoords(self.pos)[0], game.getCoords(self.pos)[1]
        self.velocity = pg.Vector2(0,0) if not velocity else velocity
        # Appearance
        self.rect = pg.Rect(self.x,self.y,game.playfield.rectSize[0],game.playfield.rectSize[1])
        self.color, self.colorKey = color, get_key(color, snakeColors)
        self.angle = 0
        self.rotateSprite()
        # State
        self.alive, self.changedDirection = True, False
    def changeDirToAnAngle(self, angle:int in range(0,361)):
        """
        Changes the velocity of the head to an absolute angle.
        """
        if angle == 0 and self.velocity.x >= 0: (self.velocity.y, self.velocity.x, self.angle) = (0, self.velocity.length(),angle)
        if angle == 90 and self.velocity.y <= 0: (self.velocity.y, self.velocity.x, self.angle) = (-self.velocity.length(), 0,angle)
        if angle == 180 and self.velocity.x <= 0: (self.velocity.y, self.velocity.x, self.angle) = (0, -self.velocity.length(),angle)
        if angle == 270 and self.velocity.y >= 0: (self.velocity.y, self.velocity.x, self.angle) = (self.velocity.length(), 0,angle)
        return self
    def rotateSprite(self):
        deg = self.angle
        if self.type == 'head':
            if deg == 0: self.loadPartImage(pilImageToSurface(partColoredImgs['headRight'][self.colorKey]))
            if deg == 90: self.loadPartImage(pilImageToSurface(partColoredImgs['headUp'][self.colorKey]))
            if deg == 180: self.loadPartImage(pilImageToSurface(partColoredImgs['headLeft'][self.colorKey]))
            if deg == 270: self.loadPartImage(pilImageToSurface(partColoredImgs['headDown'][self.colorKey]))
            return self
        if self.type == 'tail':
            if deg == 0: self.loadPartImage(pilImageToSurface(partColoredImgs['tailLeft'][self.colorKey]))
            if deg == 90: self.loadPartImage(pilImageToSurface(partColoredImgs['tailDown'][self.colorKey]))
            if deg == 180: self.loadPartImage(pilImageToSurface(partColoredImgs['tailRight'][self.colorKey]))
            if deg == 270: self.loadPartImage(pilImageToSurface(partColoredImgs['tailUp'][self.colorKey]))
        turn = self.isTurning()
        if turn:
            if turn == 1: self.loadPartImage(pilImageToSurface(partColoredImgs['topRight'][self.colorKey]))
            if turn == 2: self.loadPartImage(pilImageToSurface(partColoredImgs['bottomRight'][self.colorKey]))
            if turn == 3: self.loadPartImage(pilImageToSurface(partColoredImgs['topLeft'][self.colorKey]))
            if turn == 4: self.loadPartImage(pilImageToSurface(partColoredImgs['bottomLeft'][self.colorKey]))
            return self
        if self.type == 'body':
            if deg == 0 or deg == 180: self.loadPartImage(pilImageToSurface(partColoredImgs['bodyHor'][self.colorKey]))
            if deg == 90 or deg == 270: self.loadPartImage(pilImageToSurface(partColoredImgs['bodyVer'][self.colorKey]))
        return self
    def loadPartImage(self, img):
        self.sprite = pg.transform.scale(img,(playfield.rectSize[0]*1.02, playfield.rectSize[1]*1.02))
        return self
    def getRelatedSnakeParts(self):
        self.relatedSnakeParts = [x for x in game.snakeParts if x.snakeIndex == self.snakeIndex]
        return self
    def getAngle(self):
        if(self.velocity.x > 0): self.angle = 0
        if(self.velocity.x < 0): self.angle = 180
        if(self.velocity.y < 0): self.angle = 90
        if(self.velocity.y > 0): self.angle = 270
        return self
    def isTurning(self):
        self.getRelatedSnakeParts()
        relatedParts = self.relatedSnakeParts
        if not self in relatedParts: relatedParts.append(self)
        partIndex = relatedParts.index(self)
        if partIndex == 0 or partIndex == len(self.relatedSnakeParts)-1: return False
        prevPart, nextPart =  relatedParts[partIndex+1], relatedParts[partIndex-1]
        if (prevPart.pos == (self.pos[0]+1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]-1)) or (prevPart.pos ==(self.pos[0], self.pos[1]-1) and nextPart.pos == (self.pos[0]+1, self.pos[1])): return 1
        if game.portalWalls:
            if (prevPart.pos == (self.pos[0], self.pos[1]-1) and nextPart.pos == (self.pos[0]+1-playfield.rectDims[0], self.pos[1])) or (prevPart.pos == (self.pos[0]+1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]-1+playfield.rectDims[1])): return 1
            if (nextPart.pos == (self.pos[0], self.pos[1]-1) and prevPart.pos == (self.pos[0]+1-playfield.rectDims[0], self.pos[1])) or (nextPart.pos == (self.pos[0]+1, self.pos[1]) and prevPart.pos == (self.pos[0], self.pos[1]-1+playfield.rectDims[1])): return 1
        if (prevPart.pos == (self.pos[0]+1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]+1)) or (prevPart.pos ==(self.pos[0], self.pos[1]+1) and nextPart.pos == (self.pos[0]+1, self.pos[1])): return 2
        if game.portalWalls:
            if (prevPart.pos == (self.pos[0]+1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]+1-playfield.rectDims[1])) or (prevPart.pos == (self.pos[0], self.pos[1]+1) and nextPart.pos == (self.pos[0]+1-playfield.rectDims[0], self.pos[1])): return 2
            if (nextPart.pos == (self.pos[0]+1, self.pos[1]) and prevPart.pos == (self.pos[0], self.pos[1]+1-playfield.rectDims[1])) or (nextPart.pos == (self.pos[0], self.pos[1]+1) and prevPart.pos == (self.pos[0]+1-playfield.rectDims[0], self.pos[1])): return 2
        if (prevPart.pos == (self.pos[0]-1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]-1)) or (prevPart.pos ==(self.pos[0], self.pos[1]-1) and nextPart.pos == (self.pos[0]-1, self.pos[1])): return 3
        if game.portalWalls:
            if (prevPart.pos ==(self.pos[0]-1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]-1+playfield.rectDims[1])) or (prevPart.pos ==(self.pos[0], self.pos[1]-1) and nextPart.pos == (self.pos[0]-1+playfield.rectDims[0], self.pos[1])): return 3
            if (nextPart.pos ==(self.pos[0]-1, self.pos[1]) and prevPart.pos == (self.pos[0], self.pos[1]-1+playfield.rectDims[1])) or (nextPart.pos ==(self.pos[0], self.pos[1]-1) and prevPart.pos == (self.pos[0]-1+playfield.rectDims[0], self.pos[1])): return 3
        if (prevPart.pos == (self.pos[0]-1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]+1)) or (prevPart.pos ==(self.pos[0], self.pos[1]+1) and nextPart.pos == (self.pos[0]-1, self.pos[1])): return 4
        if game.portalWalls:
            if (prevPart.pos == (self.pos[0]-1, self.pos[1]) and nextPart.pos == (self.pos[0], self.pos[1]+1-playfield.rectDims[1])) or (prevPart.pos == (self.pos[0], self.pos[1]+1) and nextPart.pos == (self.pos[0]-1+playfield.rectDims[0], self.pos[1])): return 4
            if (nextPart.pos == (self.pos[0]-1, self.pos[1]) and prevPart.pos == (self.pos[0], self.pos[1]+1-playfield.rectDims[1])) or (nextPart.pos == (self.pos[0], self.pos[1]+1) and prevPart.pos == (self.pos[0]-1+playfield.rectDims[0], self.pos[1])): return 4
        return False

class Game:
    def __init__(self, caption:string, icon:Path, resolution:tuple, font:string, playfield:Playfield):
        """
        The game.
        """
        pg.init()
        pg.display.set_caption(caption)
        self.gameOverFont, self.scoreFont, self.menuFont, self.scoreboardFont  = pg.font.SysFont(font, gameOverFontSize), pg.font.SysFont(font, scoreFontSize), pg.font.SysFont(font, menuFontSize),pg.font.SysFont(font, scoreboardFontSize)
        pg.font.init()
        self.gameIcon = pg.image.load(icon)
        self.screen = pg.display.set_mode(resolution, pg.FULLSCREEN if fullscreen else 0)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pg.display.get_window_size()[0], pg.display.get_window_size()[1]
        # Settings
        self.background, self.multiplayer, self.portalWalls, self.speedIncAfterEat, self.initialSpeed, self.foodCount, self.poisonousFoodCount, self.foodLimit, self.poisonousFoodRespawn = background, multiplayer, portalWalls, speedIncAfterEat, initialSpeed, foodCount,poisonousFoodCount,foodLimit,poisonousFoodRespawn
        self.getMovementPeriod()
        # Playfield
        self.wallWidth, self.wallHeight = wallWidth, wallHeight
        self.sidePadding, self.topPadding = round((1-playfieldSize[0])/2, 3), round((1-playfieldSize[1])/2, 3)
        self.topBorder = pg.Rect(self.SCREEN_WIDTH*self.sidePadding,self.SCREEN_HEIGHT*(self.topPadding)+self.SCREEN_HEIGHT*playfieldYOffset-self.wallHeight,self.SCREEN_WIDTH*playfieldSize[0],self.wallHeight)
        self.bottomBorder = pg.Rect(self.SCREEN_WIDTH*self.sidePadding,self.SCREEN_HEIGHT*(playfieldSize[1]+self.topPadding)+self.SCREEN_HEIGHT*playfieldYOffset,self.SCREEN_WIDTH*playfieldSize[0],self.wallHeight)
        self.leftBorder = pg.Rect(self.SCREEN_WIDTH*self.sidePadding-self.wallWidth,self.SCREEN_HEIGHT*self.topPadding+self.SCREEN_HEIGHT*playfieldYOffset-self.wallHeight,self.wallWidth,self.SCREEN_HEIGHT*(playfieldSize[1])+self.wallHeight*2)
        self.rightBorder = pg.Rect(self.SCREEN_WIDTH*(playfieldSize[0]+self.sidePadding),self.SCREEN_HEIGHT*self.topPadding+self.SCREEN_HEIGHT*playfieldYOffset-self.wallHeight,self.wallWidth,self.SCREEN_HEIGHT*playfieldSize[1]+self.wallHeight*2)
        self.snakeParts, self.foods, self.events, self.availablePositions = [],[],[],[]
        self.playfield = playfield
        self.topWallSprite = pg.transform.smoothscale(pg.image.load(wall).convert_alpha(), (self.topBorder.w,self.topBorder.h))
        self.bottomWallSprite = pg.transform.scale(pg.image.load(wall).convert_alpha(), (self.bottomBorder.w,self.bottomBorder.h))
        self.leftWallSprite = pg.transform.smoothscale(pg.image.load(sideWall).convert_alpha(), (self.leftBorder.w,self.leftBorder.h))
        self.rightWallSprite = pg.transform.scale(pg.image.load(sideWall).convert_alpha(), (self.leftBorder.w,self.leftBorder.h))
        # Get available rects
        for i, col in enumerate(playfield.rects):
            for rect in col:
                self.availablePositions.append(rect.pos)
        # State
        self.snakeAlive, self.gameWon, self.active, self.moveEventFired, self.snake1PartAddedFired, self.snake2PartAddedFired = True, False, True, False,False,False
        # Player fields
        self.score1Pos = (self.SCREEN_WIDTH*self.sidePadding-self.wallWidth,(self.SCREEN_HEIGHT*(self.topPadding)+self.SCREEN_HEIGHT*playfieldYOffset-scoreBottomPadding)/2)
        self.score2Pos = (self.SCREEN_WIDTH-self.SCREEN_WIDTH*self.sidePadding-self.wallWidth,(self.SCREEN_HEIGHT*(self.topPadding)+self.SCREEN_HEIGHT*playfieldYOffset-scoreBottomPadding)/2)
        self.player1Score, self.player2Score = 0, 0
        self.player1Color, self.player2Color = player1Color,player2Color
        self.setPlayerColorIndex()
        self.player1ChangedDir = False
        self.player2ChangedDir = False
        self.getHighscores()
        # Menu state
        self.menuPointingTo = 0
        self.player1EnteredName = ''
        self.player2EnteredName = ''
        # Events
        self.moveEvent = pg.USEREVENT + 1
        self.snake1PartAdded = pg.USEREVENT + 2
        self.snake2PartAdded = pg.USEREVENT + 3
    def setBackground(self):
        """
        Sets the background as either an icon or a color.
        """
        if type(self.background).__name__ == 'tuple': self.screen.fill(self.background)
        if type(self.background).__name__ == 'PosixPath': self.screen.blit(pg.transform.scale(pg.image.load(background).convert_alpha(), (self.SCREEN_WIDTH,self.SCREEN_HEIGHT)),(0,0))
        return self
    def update(self):
        pg.display.update()
    def getEvents(self):
        self.events = pg.event.get()
        return self
    def isEvent(self, eventType):
        for e in self.events:
            if e.type == eventType:
                return True
        return False
    def isQuit(self, isEscape:bool=False):
        """
        Checks if the player wants to exit or not by checking whether esc of exit button is pressed.
        """
        for event in self.events:
            if event.type == pg.QUIT: return True
            if hasattr(event, 'key'):
                if self.isKey(pg.K_ESCAPE) and isEscape: return True
        return False
    def isKey(self, key:pg.key):
        """
        Checks whether the given key is pressed.
        """
        for event in self.events:
            if event.type == pg.KEYDOWN:
                if event.key == key: 
                    return True
        return False
    def isAnyKey(self):
        """
        Checks whether any key is pressed.
        """
        for event in self.events:
            if event.type == pg.KEYDOWN:
                return True
        return False
    def getKey(self):
        for event in self.events:
            if event.type == pg.KEYDOWN:
                return event.unicode
        return False
    def onUpdate(self):
        """
        Does the provided things at the start of a update cycle iteration.
        """
        self.setBackground()
        self.getEvents().setPlayerColorIndex()
        return self
    def moveSnakePart(self,snakePart:SnakePart,pos:tuple,velocity:pg.Vector2=False):
        """
        Moves snake part to the given position.
        It can also set the velocity of the snake part if provided.        
        """
        if not self.isSnakeDead():
            if velocity:
                if velocity.x > 0: xMove = 1
                elif velocity.x < 0: xMove = -1
                else: xMove = 0
                if velocity.y > 0: yMove = 1
                elif velocity.y < 0: yMove = -1
                else: yMove = 0
            else:
                yMove, xMove = 0, 0
            if (snakePart.pos[0]+xMove not in range(0, rectDims[0]) or snakePart.pos[1]+yMove not in range(0, rectDims[1])) and not self.portalWalls:
                snakePart.alive = False
            else:
                newXPos, newYPos = int(pos[0]+xMove), int(pos[1]+yMove)
                if newXPos >= rectDims[0]: newXPos -= rectDims[0]
                if newXPos < 0: newXPos += rectDims[0]
                if newYPos >= rectDims[1]: newYPos -= rectDims[1]
                if newYPos < 0: newYPos += rectDims[1]
                self.availablePositions.append(snakePart.pos)
                snakePart.pos = (newXPos, newYPos)
                self.availablePositions.remove((pos[0],pos[1]))
                snakeCoords = self.getCoords(snakePart.pos)
                snakePart.x, snakePart.y = snakeCoords
                (snakePart.rect.x, snakePart.rect.y) = snakeCoords
                snakePart.prevMoveMoment = t.time()
    def getCoords(self,pos:tuple):
        return (self.playfield.rects[pos[0]][pos[1]].x,self.playfield.rects[pos[0]][pos[1]].y+self.SCREEN_HEIGHT*playfieldYOffset)
    def createFood(self, isPoisonous:bool):
        food = Food(isPoisonous)
        self.foods.append(food)
        self.availablePositions.remove(food.pos)
        return self
    def createSnakePart(self,type:string,snakeIndex:int,color:tuple,pos:tuple=False,velocity:pg.Vector2=False,intialCreate:bool=False):
        snakePart = SnakePart(type,snakeIndex,color,pos if pos else False, velocity if velocity else False)
        self.snakeParts.append(snakePart)
        if snakePart.pos in self.availablePositions:
            self.availablePositions.remove(snakePart.pos)
            if not snakePart.pos[0] == rectDims[0]-1 and intialCreate and (snakePart.pos[0]+1,snakePart.pos[1]) in self.availablePositions: self.availablePositions.remove((snakePart.pos[0]+1,snakePart.pos[1]))
        return snakePart
    def checkRectalCollision(self,pos1:tuple,pos2:tuple):
        if pos1[0] == pos2[0] and pos1[1] == pos2[1]: return True
        else: return False
    def getRandomAvailablePos(self, xRange:range=False):
        if len(self.availablePositions) == 0: return False
        if xRange: availablePositions = [x for x in self.availablePositions if x[0] in range(xRange[0],xRange[1])]
        else: availablePositions = self.availablePositions
        return rd.choice(availablePositions)
    def getRandomFood(self, isPoisonous:bool=False):
        if isPoisonous:
            return rd.choice([x for x in self.foods if x.type == 'poison'])
        if not isPoisonous:
            return rd.choice([x for x in self.foods if x.type == 'food'])
    def isSnakeDead(self):
        if self.multiplayer: 
            snake1Alive = True if len([x for x in self.snakeParts if x.alive == False and x.snakeIndex == 0]) > 0 else False
            snake2Alive = True if len([x for x in self.snakeParts if x.alive == False and x.snakeIndex == 1]) > 0 else False
            return False if not snake1Alive and not snake2Alive else True
        return True if len([x for x in self.snakeParts if x.alive == False]) > 0 else False
    def getPlayersScore(self):
        self.player1Score = len([x for x in self.snakeParts if x.snakeIndex == 0])-1
        self.player2Score = len([x for x in self.snakeParts if x.snakeIndex == 1])-1
        return self
    def setBaseVelocity(self):
        """
        Sets the starting velocity of all starting parts of snakes.
        """
        for part in self.snakeParts: 
            part.velocity = pg.Vector2(snakeBaseVelocity)
    def createMenuItem(self,text:string,color:tuple=menuFontColor):
        return self.menuFont.render(text,True,color)
    def showMenuItems(self,items:List[pg.Surface],caret:bool=True):
        """
        Displays the given menu items.
        """
        heights, margins = 0, 0
        for i,it in enumerate(items):
            heights += it.get_height()
            if i != 0: margins += 1
        height = heights + margins*menuItemMargin
        topMargin = (self.SCREEN_HEIGHT-height)/2
        for i,it in enumerate(items):
            offset = (menuItemMargin * i) + (it.get_height()*i) if i != 0 else 0
            if self.menuPointingTo == i and caret:
                pointerCoords = (self.SCREEN_WIDTH/2-it.get_width()/2-pointerSize[0]- pointerLeftMargin, topMargin+offset+pointerSize[1]/4)
                pg.draw.polygon(self.screen,menuFontColor,[(pointerCoords[0],pointerCoords[1]), (pointerCoords[0]+pointerSize[0]*pointerSizeMult,pointerCoords[1]+pointerSize[0]*pointerSizeMult), (pointerCoords[0],pointerCoords[1]+pointerSize[1]*pointerSizeMult)])
            self.screen.blit(it, (self.SCREEN_WIDTH/2-it.get_width()/2, topMargin+offset))
        return self
    def getAvailablePlayerColors(self):
        if self.multiplayer: return [x for x in snakeColors.values() if x != self.player1Color and x != self.player2Color]
        else: return [x for x in snakeColors.values() if x != self.player1Color]
    def setPlayerColorIndex(self):
        self.player1ColorIndex = list(snakeColors.values()).index(self.player1Color)
        self.player2ColorIndex = list(snakeColors.values()).index(self.player2Color)
        return self
    def getPlayerNextColor(self,playerIndex:int in range(0,2)):
        availableColors = self.getAvailablePlayerColors()
        playerColorIndex = self.player1ColorIndex if playerIndex == 0 else self.player2ColorIndex
        nextColor = False
        while not nextColor:
            allColors = list(snakeColors.values())
            if len(allColors) > playerColorIndex+1:
                color = allColors[playerColorIndex+1]
                if color in availableColors:
                    nextColor = color
            elif allColors[0] not in availableColors:
                nextColor = allColors[1]
            else:
                nextColor = allColors[0]
            playerColorIndex += 1
        if playerIndex == 0: self.player1Color = nextColor
        else: self.player2Color = nextColor
        return self
    def setConfig(self,section,field,val):
        config.set(section,field, val)
        with open(configFile, 'w') as cf:
            config.write(cf)
        return self
    def getMovementPeriod(self):
        self.movementPeriod = initialMovementPeriod - ((self.initialSpeed-1) * speedUnit)
        return self
    def getNextPartPos(self, pos:tuple, velocity:pg.Vector2):
        return (int(pos[0]+velocity.x),int(pos[1]+velocity.y))
    def isSnakePartOnPos(self,pos:tuple,snakeIndex:int):
        for part in game.snakeParts:
            if part.type == 'head' and part.snakeIndex == snakeIndex: continue
            if part.pos == pos: return True
        return False
    def getHighscores(self):
        with open(spHighcoreFile,"rb") as f:
            self.singleplayerHighscores = pc.load(f)
        with open(mpHighcoreFile,"rb") as f:
            self.multiplayerHighscores = pc.load(f)
    def storeScore(self,nickname:string,score:int,nickname_:string=False,score_:int=False):
        self.getHighscores()
        if not game.multiplayer:
            with open(spHighcoreFile,"wb") as f:
                pickler = pc.Pickler(f)
                dublicate = False
                for x in self.singleplayerHighscores:
                    record = self.singleplayerHighscores[x]
                    if record['nickname'] == nickname: dublicate = record
                if dublicate:
                    dublicateRecord = self.singleplayerHighscores[get_key(dublicate, self.singleplayerHighscores)]
                    if dublicateRecord['score']<score:
                        dublicateRecord['nickname'] = nickname
                        dublicateRecord['score'] = score
                else:
                    id = rd.randint(111111,999999)
                    self.singleplayerHighscores[id] = {'nickname':nickname,'score': score}
                pickler.dump(self.singleplayerHighscores)
        if game.multiplayer:
            with open(mpHighcoreFile,"wb") as f:
                pickler = pc.Pickler(f)
                dublicate = False
                for x in self.multiplayerHighscores:
                    record = self.multiplayerHighscores[x]
                    if record['nickname'] == nickname and record['nickname_'] == nickname_: dublicate = record
                if dublicate:
                    dublicateRecord = self.multiplayerHighscores[get_key(dublicate, self.multiplayerHighscores)]
                    recScoreSum = dublicateRecord['score'] + dublicateRecord['score_']
                    scoreSum = score + score_
                    if recScoreSum < scoreSum:
                        dublicateRecord['nickname'] = nickname
                        dublicateRecord['score'] = score
                        dublicateRecord['nickname_'] = nickname_
                        dublicateRecord['score_'] = score_
                else:
                    id = rd.randint(111111,999999)
                    self.multiplayerHighscores[id] = {'nickname':nickname,'score': score, 'nickname_':nickname_,'score_':score_}
                pickler.dump(self.multiplayerHighscores)
        return self

# Game initialization
playfieldWidth, playfieldHeight = res[0] * playfieldSize[0], res[1] * playfieldSize[1]
playfield = Playfield(rectDims, (playfieldWidth, playfieldHeight), playfieldSize)
game = Game(caption,gameIcon,res,font,playfield)
