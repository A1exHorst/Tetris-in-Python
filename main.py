'''
Tetris made with pygame by Alexander Horst
Controls:
       y        - Rotates the piece counterclockwise
       ↑ or x   - Rotates the piece clockwise
    ←     →     - Move the piece to the left or to the right
       ↓        - Increases the falling speed of the block
     space      - Instantly puts the block on the ground
       c        - Puts the current block on the Clipboard for later use
                  using c again therefore switches the block with the block on the clipboard
'''

import os
import time

import pygame as pg
import random
import math

import pygame.font

pg.init()
pg.display.set_caption("Tetris in Python")

# Game settings
BOARD_LENGTH = 10
BOARD_HEIGHT = 19
SHOWCASE_LENGTH = 5
SHOWCASE_HEIGHT = 14
FIELD_SIZE = 40
FIELD_COLOR_BRIGHT = (32, 32, 64)  # (32, 0, 64)
FIELD_COLOR_DARK = (16, 16, 16)  # (48, 0, 96)
FIELD_OFFSET_X = FIELD_SIZE  # SCREEN_WIDTH / 2 - FIELD_SIZE * BOARD_LENGTH / 2
SCREEN_WIDTH = FIELD_SIZE * BOARD_LENGTH + FIELD_SIZE * 6
SCREEN_HEIGHT = FIELD_SIZE * BOARD_HEIGHT
SCREEN_COLOR = (32, 0, 64)
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FALLSPEED_DEFAULT = 1000  # In milliseconds
VOLUME = 0.1
points = 0

magicText_Offset = 0
magicText_speed = 5
magicText_tick = 0

holdingText_font = pygame.font.Font(os.path.join(os.getcwd(), "minecraft.ttf"), FIELD_SIZE)
holdingText_surface = holdingText_font.render("holding", True, (255, 255, 255))
points_labelText_font = pygame.font.Font(os.path.join(os.getcwd(), "minecraft.ttf"), FIELD_SIZE)
magicText_font = pygame.font.Font(os.path.join(os.getcwd(), "minecraft-enchantment.ttf"), FIELD_SIZE)  # Wierd
magicText = "Made By Alexander Horst "

# Each block has its own color
formToColor = [(64, 64, 192),
               (192, 128, 0),
               (0, 0, 192),
               (128, 0, 0),
               (0, 128, 0),
               (128, 0, 128),
               (128, 128, 0)]
formToCenter = [2, 1, 2, 2, 2, 2, 0]


def playSound(path: str):
    sound = pg.mixer.Sound(path)
    sound.set_volume(VOLUME)
    sound.play()

class Field:
    def __init__(self, x, y):
        self.rect = pg.Rect((x, y, FIELD_SIZE, FIELD_SIZE))
        self.color = (32, 0, 64)
        self.state = False  # If True, the block is hard and interacts with the falling piece


class Piece:

    def __init__(self):
        self.pos = None  # The positions of each block
        self.color = None  # The color of each block
        self.center = None  # Center block around which the piece rotates
        self.form = None  # Tells which kind of piece the block is
        self.copyForm = None  # The form of the saved block
        self.switchedForm = False  # True if the player already selected the other block

    def spawnPiece(self, forBoard):
        if self.form != None:
            playSound("sounds/drop.mp3")
        self.form = random.randint(0, 6)
        self.dropPiece(forBoard)
        self.switchedForm = False

    def switchPiece(self):
        if self.switchedForm == False:
            if self.copyForm == None:
                self.copyForm = random.randint(0, 6)
            self.switchedForm = True
            f = self.form
            holdingBlock.form = self.form
            holdingBlock.dropPiece(False)
            self.form = self.copyForm
            self.copyForm = f
            self.dropPiece(True)

    def dropPiece(self, forBoard):
        self.color = formToColor[self.form]
        self.center = formToCenter[self.form]
        if not forBoard:  # Block positions for the showcase
            if self.form == 0:
                self.pos = [[2, 1], [2, 2], [2, 3], [2, 4]]
            elif self.form == 1:
                self.pos = [[1, 3], [2, 3], [3, 3], [3, 2]]
            elif self.form == 2:
                self.pos = [[1, 2], [1, 3], [2, 3], [3, 3]]
            elif self.form == 3:
                self.pos = [[1, 2], [2, 2], [2, 3], [3, 3]]
            elif self.form == 4:
                self.pos = [[2, 2], [3, 2], [2, 3], [1, 3]]
            elif self.form == 5:
                self.pos = [[2, 2], [1, 3], [2, 3], [3, 3]]
            else:
                self.pos = [[1, 2], [2, 2], [1, 3], [2, 3]]
        else:  # Block positions for the game board
            if self.form == 0:
                self.pos = [[4, 0], [4, 1], [4, 2], [4, 3]]
            elif self.form == 1:
                self.pos = [[3, 1], [4, 1], [5, 1], [5, 0]]
            elif self.form == 2:
                self.pos = [[3, 0], [3, 1], [4, 1], [5, 1]]
            elif self.form == 3:
                self.pos = [[4, 0], [5, 0], [5, 1], [6, 1]]
            elif self.form == 4:
                self.pos = [[4, 0], [5, 0], [4, 1], [3, 1]]
            elif self.form == 5:
                self.pos = [[5, 0], [4, 1], [5, 1], [6, 1]]
            else:
                self.pos = [[4, 0], [5, 0], [4, 1], [5, 1]]

    def copy(self):
        copy = Piece()
        copy_pos = []
        for i in range(len(self.pos)):
            temp = []
            for j in range(len(self.pos[i])):
                temp.append(self.pos[i][j])
            copy_pos.append(temp)
        copy.pos = copy_pos
        copy.color = self.color
        copy.center = self.center
        copy.form = self.form
        copy.copyForm = self.copyForm
        copy.switchedForm = self.switchedForm
        return copy


fields = []
for x in range(BOARD_LENGTH):
    y_array = []
    for y in range(BOARD_HEIGHT):
        y_array.append(Field(x * FIELD_SIZE + FIELD_OFFSET_X, y * FIELD_SIZE))
    fields.append(y_array)

showcaseFields = []
for x in range(SHOWCASE_LENGTH):
    y_array = []
    for y in range(SHOWCASE_HEIGHT):
        y_array.append(Field(BOARD_LENGTH * FIELD_SIZE + FIELD_OFFSET_X + x * FIELD_SIZE, y * FIELD_SIZE))
        y_array[y].color = (32, 32, 32)
    showcaseFields.append(y_array)

fallingBlock = Piece()
holdingBlock = Piece()
shadowBlock = Piece()

fallingBlock.spawnPiece(True)

FALLSPEED = FALLSPEED_DEFAULT
ROTATIONSPEED = random.randint(500, 2000)
ROTATIONPATTERN_DEFAULT = [0, 0, 0, 1, 1, 1]  # 0 = False(Counter Clockwise)   1 = True(Clockwise)
ROTATIONPATTERN = ROTATIONPATTERN_DEFAULT
run = True
dropTick = pg.time.get_ticks()
rotationTick = pg.time.get_ticks()


def rotate(block, direction, careForCollision):
    if block.form != 6:
        posList = []
        for i in range(len(block.pos)):
            if block.center != i:
                x = block.pos[i][0]
                y = block.pos[i][1]
                newX = None
                newY = None
                if x - block.pos[block.center][0] == 0:
                    # Orange
                    distanceY = y - block.pos[block.center][1]
                    if direction:
                        newX = x + (-distanceY)
                    else:
                        newX = x + distanceY
                    newY = block.pos[block.center][1]
                elif y - block.pos[block.center][1] == 0:
                    # Rot
                    distanceX = x - block.pos[block.center][0]
                    newX = block.pos[block.center][0]
                    if direction:
                        newY = y + distanceX
                    else:
                        newY = y - distanceX
                else:
                    # Lila
                    distanceX = x - block.pos[block.center][0]
                    distanceY = y - block.pos[block.center][1]
                    if direction:
                        newX = block.pos[block.center][0] + (-distanceY)
                        newY = block.pos[block.center][1] + distanceX
                    else:
                        newX = block.pos[block.center][0] + distanceY
                        newY = block.pos[block.center][1] - distanceX
                pos = [newX, newY]
                posList.append(pos)
            else:
                posList.append(block.pos[block.center])
        collision = False
        if careForCollision:
            for pos in posList:
                if pos[0] < 0 or pos[0] >= BOARD_LENGTH or pos[1] >= BOARD_HEIGHT:
                    collision = True
                    break
                if fields[pos[0]][pos[1]].state == True:
                    collision = True
                    break
        if collision == False:
            if careForCollision:
                playSound("sounds/rotate.mp3")
            for i in range(len(block.pos)):
                block.pos[i] = posList[i]
    return block


def approachingImpact(block: Piece):  # returns 1 if Block is about to touch the Border or another Block
    for pos in block.pos:
        if pos[1] == BOARD_HEIGHT - 1:
            return 1

        elif fields[pos[0]][pos[1] + 1].state == True:
            return 1
    return 0


def bordersTouched():  # Checks if the block is touching the game borders
    for pos in fallingBlock.pos:
        if pos[0] == 0:
            return -1
        elif pos[0] == BOARD_LENGTH - 1:
            return 1
    return 0


def hardBlockTouched(block: Piece):  # Returns an array which tells you which sides are touched. 1 Means its touched
    temp = [0, 0]

    for pos in block.pos:
        if pos[0] != 0:
            if fields[pos[0] - 1][pos[1]].state == True:
                temp = [1, temp[1]]
        if pos[0] != BOARD_LENGTH - 1:
            if fields[pos[0] + 1][pos[1]].state == True:
                temp = [temp[0], 1]
    return temp


playSound("sounds/game_start.mp3")

# In pygame, the game itself is always in a while loop
while run:
    posX_array = []
    posY_array = []
    for temp in fallingBlock.pos:
        posX_array.append(temp[0])
        posY_array.append(temp[1])
    fallingBlockPos = [posX_array, posY_array]  # Same information as fallingBlock.pos but in a different format

    if pg.time.get_ticks() - dropTick >= FALLSPEED:  # Drops the falling block one by one
        dropTick = pg.time.get_ticks()
        if approachingImpact(fallingBlock) == 0:  # The block is not approaching impact
            i = 0
            for pos in fallingBlock.pos:
                pos[1] = pos[1] + 1
                fallingBlock.pos[i] = pos
                i += 1
        else:  # The block fell on the ground or on another block, it hardens and tries to spawn another
            for pos in fallingBlock.pos:
                fields[pos[0]][pos[1]].state = True
            fallingBlock.spawnPiece(True)
            for pos in fallingBlock.pos:
                if fields[pos[0]][pos[1]].state == True:
                    run = False

    # Rotates the block in the holding slot, this is just an overcomplicated cosmetic
    if pg.time.get_ticks() - rotationTick >= ROTATIONSPEED and not holdingBlock.pos == None:
        ROTATIONSPEED = random.randint(500, 2000)
        rotationTick = pg.time.get_ticks()
        rd = random.randint(0, len(ROTATIONPATTERN) - 1)  # 6
        holdingBlock = rotate(holdingBlock, ROTATIONPATTERN[rd], False)
        countedZeros = 0
        for direction in ROTATIONPATTERN:
            if direction == 0:
                countedZeros += 1
        if not (countedZeros == 0 or countedZeros == 6):
            newPattern = []
            if ROTATIONPATTERN[rd]:
                for newDirection in range(len(ROTATIONPATTERN)):
                    if newDirection < countedZeros - 1:
                        newPattern.append(0)
                    else:
                        newPattern.append(1)
            else:
                for newDirection in range(len(ROTATIONPATTERN)):
                    if newDirection < countedZeros + 1:
                        newPattern.append(0)
                    else:
                        newPattern.append(1)
            ROTATIONPATTERN = newPattern
        else:
            ROTATIONPATTERN = ROTATIONPATTERN_DEFAULT

    # This loop checks if there are any completed lines
    linesClearedAtY = []
    for y in range(BOARD_HEIGHT):
        lineIsComplete = True
        for x in range(BOARD_LENGTH):
            if fields[x][y].state == False:  # If there is a hole in one row, the line isn't complete
                lineIsComplete = False
        if lineIsComplete:
            linesClearedAtY.append(y)
            points += 1  # Each full line gives 1 point
    # This loop removes all completed lines and pulls the ones on top of it down
    for y in linesClearedAtY:
        for y2 in range(y + 1):
            y3 = y - y2
            if y3 == 0:
                break
            for x in range(BOARD_LENGTH):
                pixelIsFromFallingBlock = False
                for pos in fallingBlock.pos:
                    if x == pos[0] and y3 - 1 == pos[1]:
                        pixelIsFromFallingBlock = True
                if not pixelIsFromFallingBlock:
                    fields[x][y3].color = fields[x][y3 - 1].color
                    fields[x][y3].state = fields[x][y3 - 1].state
    if len(linesClearedAtY) != 0:   # Play a sound if a line is cleared
        playSound("sounds/clear.mp3")
    # Painting the Board, which is a chess like background but with a color fade
    for x in range(BOARD_LENGTH):
        for y in range(BOARD_HEIGHT):
            if fields[x][y].state == False:
                if y // 2 - y / 2 == 0:
                    if x // 2 - x / 2 == 0:
                        fields[x][y].color = (FIELD_COLOR_BRIGHT[0] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_BRIGHT[1] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_BRIGHT[2] * ((255 - (255 / BOARD_HEIGHT) * y) / 255))
                    else:
                        fields[x][y].color = (FIELD_COLOR_DARK[0] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_DARK[1] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_DARK[2] * ((255 - (255 / BOARD_HEIGHT) * y) / 255))
                else:
                    if x // 2 - x / 2 == 0:
                        fields[x][y].color = (FIELD_COLOR_DARK[0] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_DARK[1] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_DARK[2] * ((255 - (255 / BOARD_HEIGHT) * y) / 255))
                    else:
                        fields[x][y].color = (FIELD_COLOR_BRIGHT[0] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_BRIGHT[1] * ((255 - (255 / BOARD_HEIGHT) * y) / 255),
                                              FIELD_COLOR_BRIGHT[2] * ((255 - (255 / BOARD_HEIGHT) * y) / 255))

    # Adds the Shadow block to the board
    shadowBlock = fallingBlock.copy()
    shadowBlock.color = (shadowBlock.color[0] / 3, shadowBlock.color[1] / 3, shadowBlock.color[2] / 3)  # Darker color
    while approachingImpact(shadowBlock) == 0:
        i = 0
        for pos in shadowBlock.pos:
            pos[1] = pos[1] + 1
            shadowBlock.pos[i] = pos
            i += 1
    for pos in shadowBlock.pos:
        fields[pos[0]][pos[1]].color = shadowBlock.color

    # Changes the fields data based on where the falling block is
    for pos in fallingBlock.pos:
        fields[pos[0]][pos[1]].color = fallingBlock.color

    screen.fill(SCREEN_COLOR)  # Game background color

    # Painting the whole game board
    for x in range(BOARD_LENGTH):
        for y in range(BOARD_HEIGHT):
            pg.draw.rect(screen, fields[x][y].color, fields[x][y])

    # This part is for the Showcase screen
    # Background
    for x in range(SHOWCASE_LENGTH):
        for y in range(5):
            showcaseFields[x][y + 1].color = (16, 16, 16)
    # The block on showcase
    if not holdingBlock.pos == None:
        for pos in holdingBlock.pos:
            showcaseFields[pos[0]][pos[1]].color = holdingBlock.color
    # Printing the Showcase
    for x in range(SHOWCASE_LENGTH):
        for y in range(SHOWCASE_HEIGHT):
            pg.draw.rect(screen, showcaseFields[x][y].color, showcaseFields[x][y])

    # This area is about refreshing all the blocks and texts
    screen.blit(holdingText_surface, (FIELD_OFFSET_X + FIELD_SIZE * BOARD_LENGTH, 0))
    points_labelText_surface = points_labelText_font.render("points:", True, (255, 255, 255))
    screen.blit(points_labelText_surface, (FIELD_OFFSET_X + FIELD_SIZE * BOARD_LENGTH, FIELD_SIZE * 14))
    points_content_surface = points_labelText_font.render(str(points), True, (255, 255, 255))
    screen.blit(points_content_surface, (FIELD_OFFSET_X + FIELD_SIZE * BOARD_LENGTH, FIELD_SIZE * 15))
    # For the magic Text on the left
    if pg.time.get_ticks() - magicText_tick >= magicText_speed:
        magicText_tick = pg.time.get_ticks()
        magicText_Offset += 1
        if magicText_Offset > FIELD_SIZE:
            magicText_Offset = 0
            magicText = magicText[len(magicText) - 1] + magicText[0:len(magicText) - 1]
    for letterIdx in range(len(magicText)):
        magicText_surface = magicText_font.render(magicText[letterIdx], True, (255, 255, 255))
        screen.blit(magicText_surface, (0, FIELD_SIZE * (letterIdx - 1) + magicText_Offset))
    magicText_Border = Field(0, FIELD_SIZE * BOARD_HEIGHT)
    pg.draw.rect(screen, SCREEN_COLOR, magicText_Border)

    # This area is about reading player input
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                if bordersTouched() != -1 and hardBlockTouched(fallingBlock)[0] == 0:
                    playSound("sounds/move.mp3")
                    i = 0
                    for pos in fallingBlock.pos:
                        pos[0] = pos[0] - 1
                        fallingBlock.pos[i] = pos
                        i += 1
            if event.key == pg.K_RIGHT:
                if bordersTouched() != 1 and hardBlockTouched(fallingBlock)[1] == 0:
                    playSound("sounds/move.mp3")
                    i = 0
                    for pos in fallingBlock.pos:
                        pos[0] = pos[0] + 1
                        fallingBlock.pos[i] = pos
                        i += 1
            if event.key == pg.K_SPACE:
                while approachingImpact(fallingBlock) == 0:
                    i = 0
                    for pos in fallingBlock.pos:
                        pos[1] = pos[1] + 1
                        fallingBlock.pos[i] = pos
                        i += 1
                for pos in fallingBlock.pos:
                    fields[pos[0]][pos[1]].color = fallingBlock.color
                for pos in fallingBlock.pos:
                    fields[pos[0]][pos[1]].state = True
                fallingBlock.spawnPiece(True)
            if event.key == pg.K_UP or event.key == pg.K_x:
                fallingBlock = rotate(fallingBlock, True, True)
            if event.key == pg.K_y:
                fallingBlock = rotate(fallingBlock, False, True)

            if event.key == pg.K_c:
                fallingBlock.switchPiece()
            if event.key == pg.K_ESCAPE:
                pg.quit()
            if event.key == pg.K_DOWN:
                FALLSPEED = 50
        if event.type == pg.KEYUP:
            if event.key == pg.K_DOWN:
                FALLSPEED = FALLSPEED_DEFAULT
    pg.display.update()

# Game Over Screen, stop everything
time.sleep(3)
pg.quit()
