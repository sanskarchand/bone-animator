#!/usr/bin/env python
import const
import pygame as pg

class Button:
    def __init__(self, pos, text):
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.width = 110
        self.height = 40
        self.text = text
        self.function = None

        self.rect = pg.Rect(self.pos_x, self.pos_y, self.width, self.height)
        self.font = pg.font.SysFont("Times New Roman", 16, bold=True)

        self.hover = False
        self.pressed = False

        self.col_normal = const.COL_BUT_NORMAL
        self.col_hover = const.COL_BUT_HOVER
        self.color = self.col_normal


    def assignCallback(self, callback):
        self.function = callback

    def checkPressed(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.pressed = True

    def checkReleased(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.pressed = False
            self.function()

            # call callback

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.hover = True
        else:
            self.pressed = False
            self.hover = False
         
        if self.hover:
            self.color = self.col_hover
        else:
            self.color = self.col_normal

    

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect)
        self.text_surf = self.font.render(self.text, False, const.COL_FONT)
        screen.blit(self.text_surf, (self.pos_x + 20, self.pos_y + 10))

        if self.pressed:
            pg.draw.rect(screen, const.COL_BUT_OUTLINE, self.rect, 4)


class ScrollArea:

    def __init__(self, pos, width, height):
        self.pos_x = pos[0]
        self.width = width
        self.height = height

    def addItem(self, item):
        pass
