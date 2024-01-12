#!/usr/bin/env python
import pygame as pg
import Bone
import const
import os
from gui.gui import GUI, Orientation
from gui.const import POS_UNDEF

# last change: 2020-11-22
class MainApplication:

    def __init__(self):
        self.running = True
        self.current_frame = 0
        self.mouse_pos = (0, 0)
        
        self.figure_def = Bone.Figure.fromFile("man_figure.xml")
        self.current_figure = self.figure_def
        self.ctrl_rect: pg.Rect | None = None

        self.init_pg()
        self.init_gui()
        
    def init_pg(self):
        pg.init()
        pg.font.init()

        self.main_screen = pg.display.set_mode(const.TOTAL_DIM)
        pg.display.set_caption("Pivot Clone")
        self.clock = pg.time.Clock()
    
    
    def init_gui(self):
        self.gui = GUI(self.main_screen)

        ## make rect

        self.ctrl_rect = pg.Rect(*const.RIGHT_CTRL_RECT_PARAMS)
        self.ctrl_container = self.gui.make_container_from_rect(
                                        self.ctrl_rect,
                                        Orientation.VERTICAL
                                    )
        
        but_frame = self.gui.make_text_button(POS_UNDEF, 160, 20, "Add Frame", self.addFrame, ())
        self.ctrl_container.push_item(but_frame)

        self.surf_canvas = pg.Surface(list(const.CANVAS_DIM), pg.SRCALPHA, 32)
        self.surf_canvas = self.surf_canvas.convert_alpha()


        self.gui.add_elem(self.ctrl_container)

    def addFrame(self):
        self.current_figure.addFrame()
        self.current_frame += 1
        print("FRAMESSSSS")

    def mainloop (self):

        while self.running:
            self.mouse_pos = pg.mouse.get_pos()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break
                else:
                    self.gui.update(event, self.mouse_pos)

                
                ## TODO: replace this with a scene manager or soemthing
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.figure_def.checkPressed(self.mouse_pos)

                if event.type == pg.MOUSEBUTTONUP:
                    self.figure_def.root.unselectGimbals()

            
            ### Wipe/Fill screen, and draw GUI
            self.main_screen.fill(const.BGCOLOR)
            pg.draw.rect(self.main_screen, const.GREY, self.ctrl_rect)
            self.gui.draw()

            self.figure_def.update()
            print("UPDATE FIN===================")
            self.figure_def.draw(self.main_screen)
            
            pg.display.update()
            self.clock.tick(const.FPS)




m_app = MainApplication()
if __name__ == "__main__":
    m_app.mainloop()
