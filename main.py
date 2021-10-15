#!/usr/bin/env python
import tkinter as tk
import pygame as pg
import Bone, Gui, const
import os
# last change: 2020-11-22
class MainApplication:

    def __init__(self):
        self.running = True
        self.current_frame = 0
        self.mouse_pos = (0, 0)
        
        self.figure_def = Bone.Figure.fromFile("man_figure.xml")
        self.current_figure = self.figure_def
        
        pg.init()
        self.main_screen = pg.display.set_mode(const.TOTAL_DIM)
        
        self.rect_canvas = pg.Rect(0, 0, const.CANVAS_DIM[0], const.CANVAS_DIM[1])

        self.surf_canvas = pg.Surface(list(const.CANVAS_DIM), pg.SRCALPHA, 32)
        self.surf_canvas = self.surf_canvas.convert_alpha()

        self.rect_ctrl_right = pg.Rect(const.CANVAS_DIM[0], 0, 
                const.TOTAL_DIM[0]-const.CANVAS_DIM[0], const.TOTAL_DIM[1]-const.CANVAS_DIM[1])
        self.rect_ctrl_bottom = pg.Rect(0, const.CANVAS_DIM[1],
                const.CANVAS_DIM[0], const.TOTAL_DIM[1]-const.CANVAS_DIM[1])
        self.rect_export = pg.Rect(*const.EXPORT_RECT)

        pg.display.set_caption("Pivot Clone")
        self.clock = pg.time.Clock()
        
        self.buttons = []
        bound_x = const.CANVAS_DIM[0]
        self.button_add_frame = Gui.Button((bound_x + 20, 20), "Add Frame")
        self.button_add_frame.assignCallback(self.addFrame)

        self.buttons.append(self.button_add_frame)


    def addFrame(self):
        self.current_figure.addFrame()
        self.current_frame += 1
        print("FRAMESSSSS")

    def exportFrame(self):
        None
    def mainLoop(self):

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.figure_def.checkPressed(self.mouse_pos)
                    for button in self.buttons:
                        button.checkPressed(self.mouse_pos)

                if event.type == pg.MOUSEBUTTONUP:
                    self.figure_def.root.unselectGimbals()
                    for button in self.buttons:
                        button.checkReleased(self.mouse_pos)

            
            self.mouse_pos = pg.mouse.get_pos()
            self.figure_def.update()
            for button in self.buttons:
                button.update(self.mouse_pos)

            self.main_screen.fill(const.GREY)
            pg.draw.rect(self.main_screen, const.BGCOLOR, self.rect_canvas)
            #self.main_screen.blit(self.surf_canvas, (0, 0))
            #pg.draw.rect(self.main_screen, const.RED, self.rect_export, 2)
            self.figure_def.draw(self.main_screen)
            for button in self.buttons:
                button.draw(self.main_screen)
            pg.display.update()
            self.clock.tick(const.FPS)




m_app = MainApplication()
m_app.mainLoop()
