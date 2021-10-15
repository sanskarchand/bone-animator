#!/usr/bin/env python
import tkinter as tk
import pygame as pg
import Bone, const
import os

class MainApplication:

    def __init__(self):
        self.running = True
        self.mouse_pos = (0, 0)
        
        self.root = tk.Tk()
        self.embed = tk.Frame(self.root, width=const.PYGAME_DIM[0],
                height=const.PYGAME_DIM[1])
        self.embed.pack(side="right")

        #Tell pygame's SDL window the window ID to be used
        os.environ["SDL_WINDOWID"] = str(self.embed.winfo_id())

        #for WINDOWS
        #os.environ["SDL_VIDEODRIVER"] = "windib"

        self.root.update()      # assign ID by showing

        self.figure_def = Bone.Figure.fromFile("man_figure.xml")

        pg.init()
        self.main_screen = pg.display.set_mode(const.PYGAME_DIM)
        self.clock = pg.time.Clock()


        self.createWidgets()

    def createWidgets(self):

        self.button = tk.Button(self.root)
        self.button["text"] = "FUCK THIS"
        self.button.pack(side="left")

    def mainLoop(self):

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.KEYDOWN:
                    print("KEY PRESSED")

                if event.type == pg.MOUSEBUTTONDOWN:
                    print("MOUSE BUTTON DOWN")
                    self.figure_def.checkPressed(self.mouse_pos)
            
            self.mouse_pos = pg.mouse.get_pos()

            self.main_screen.fill(const.BGCOLOR)

            self.figure_def.draw(self.main_screen)
            pg.display.update()
            self.clock.tick(const.FPS)

            self.root.update()



m_app = MainApplication()
m_app.mainLoop()
