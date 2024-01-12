#!/usr/bin/env python

import xml.etree.ElementTree as ET
from enum import Enum
import math
import pygame as pg
#import pygame.gfxdraw
import const

class BoneType(Enum):
    UNDEF = 0
    LINE = 1
    CIRCLE = 2

class Gimbal:
    
    def __init__(self, bone):
        self.bone = bone
        self.pos_x = self.bone.pos_x2
        self.pos_y = self.bone.pos_y2
        self.rad = 10
        self.rect = pg.Rect(self.pos_x -self.rad, self.pos_y - self.rad, 2*self.rad, 2*self.rad)

        self.visible = True
        self.selected = False
        self.color_normal = const.COL_GIMB_ROT
        self.color_selected = const.COL_GIMB_ROT_SEL

        self.color = self.color_normal

        self.old_angle = 0
        self.mouse_prev = (None, None)


    def checkPressed(self, mousePos):
        if self.selected:
            return

        if self.rect.collidepoint(mousePos):
            self.selected = True
            self.mouse_prev = mousePos

    def unselect(self):
        self.selected = False

    def update(self):
        self.pos_x = self.bone.pos_x2
        self.pos_y = self.bone.pos_y2
        self.rect = pg.Rect(self.pos_x -self.rad, self.pos_y - self.rad, 2*self.rad, 2*self.rad)

        if self.selected:
            self.color = self.color_selected
            #print("PROP ANGLE -> ", self.bone.getPropagatedAngle())
        else:
            self.color = self.color_normal
        

        if self.selected:
            cur_mouse = pg.mouse.get_pos()
            dx = cur_mouse[0] - self.bone.pos_x1
            dy = cur_mouse[1] - self.bone.pos_y1
            angle = math.atan2(-dy, dx)
            
            self.bone.angle = math.degrees(angle)

            ## if not independent, 
            if not self.bone.other_end:
                self.bone.angle -= self.bone.getPropagatedAngle()

    def draw(self, screen):
        if self.visible:
            pg.draw.circle(screen, self.color, (int(self.pos_x), int(self.pos_y)), self.rad)


class WunderGimbal(Gimbal):

    def __init__(self, bone):
        super().__init__(bone)
        self.color_normal = const.COL_GIMB_MOVE
        self.color_selected = const.COL_GIMB_MOVE_SEL
        self.pos_x = bone.pos_x1
        self.pos_y = bone.pos_y1
        self.rect = pg.Rect(self.pos_x - self.rad, self.pos_y - self.rad, 2 * self.rad, 2 * self.rad)

    def update(self):
        self.pos_x = self.bone.pos_x1
        self.pos_y = self.bone.pos_y1
        self.rect = pg.Rect(self.pos_x -self.rad, self.pos_y - self.rad, 2*self.rad, 2*self.rad)

        if self.selected:
            self.color = self.color_selected
            #print("PROP ANGLE -> ", self.bone.getPropagatedAngle())
        else:
            self.color = self.color_normal


        if self.selected:
            cur_mouse = pg.mouse.get_pos()
            dx = cur_mouse[0] - self.bone.pos_x1
            dy = cur_mouse[1] - self.bone.pos_y1
            
            self.bone.pos_x1 += dx
            self.bone.pos_y1 += dy



class Bone:

    def __init__(self, wunder=True):
        self.type = BoneType.LINE
        self.length = -1
        self.angle = 0
        self.pos_x1 = 0
        self.pos_y1 = 0
        self.pos_x2 = 0
        self.pos_y2 = 0
        self.color = (0, 0, 0)
    
        self.parent = None
        self.children = []
        self.wunderkind = False # root bone; extra gimbal (translation)

        ### e.g. torso is wunderkind, and parent of left_left and leg_right
        ###  , both of which are other_end. The legs can rotate independently of the 
        ###   torso despite their hierarchical position
        self.other_end = False  

        self.gimbal = Gimbal(self)
        self.wunder_gimbal = WunderGimbal(self)

        # animation stuff
        self.current_frame = 0
        self.frame_translations = []    # only used by root bone
        self.frame_angles = []

    def getPropagatedAngle(self):

        ang = 0
        par  = self.parent
        while par:
            ang += par.angle
            if par.other_end:
                break
            par = par.parent
        return ang
    
    def addFrame(self):
        if self.wunderkind:
            self.frame_translations.append((self.pos_x1, self.pos_x2))
        self.frame_angles.append(self.angle)

    def update(self):
        
        # account for higher/parent nodes
        if (self.parent):
            self.pos_x1 = self.parent.pos_x2
            self.pos_y1 = self.parent.pos_y2
            # special consideration for gimbals attached to wunderkind
            # set non-moving end to gimbal start
            if self.other_end:
                self.pos_x1 = self.parent.pos_x1
                self.pos_y1 = self.parent.pos_y1
       
        ang_parent = 0
        if not self.other_end:
            ang_parent = self.getPropagatedAngle()

        ang = math.radians(self.angle + ang_parent)
        self.pos_x2 = self.pos_x1 + math.cos(ang) * self.length
        self.pos_y2 = self.pos_y1 - math.sin(ang) * self.length

        self.gimbal.update()
        if self.wunderkind:
            self.wunder_gimbal.update()
        

    def updateAll(self):
        self.update()
        for child in self.children:
            child.updateAll()

        print("updateAll finished!")

    #def updateGimbals(self):
    #    self.gimbal.update()
        #for child in self.children:
        #    child.updateGimbals()

    def checkPressed(self, mousePos):
        self.gimbal.checkPressed(mousePos)
        if self.wunderkind:
            self.wunder_gimbal.checkPressed(mousePos)

        for child in self.children:
            child.checkPressed(mousePos)
    
    def unselectGimbals(self):
        self.gimbal.unselect()
        if self.wunderkind:
            self.wunder_gimbal.unselect()
        for child in self.children:
            child.unselectGimbals()

    def draw(self, screen):
        #self.update()
        if self.type == BoneType.CIRCLE:
            cx = int(self.pos_x2 + self.pos_x1)//2
            cy = int(self.pos_y2 + self.pos_y1)//2
            
            pg.draw.circle(screen, self.color, (cx, cy), int(self.length/2), 15)
        else:
            pg.draw.line(screen, self.color, (self.pos_x1, self.pos_y1),
                (self.pos_x2, self.pos_y2), 20)
            #pg.gfxdraw.line(screen, int(self.pos_x1), int(self.pos_y1), int(self.pos_x2), int(self.pos_y2), self.color)
        
        pg.draw.circle(screen, self.color, (int(self.pos_x1), int(self.pos_y1)), 10)
        pg.draw.circle(screen, self.color, (int(self.pos_x2), int(self.pos_y2)), 10)

    def drawExtra(self, screen):
        self.gimbal.draw(screen)
        if self.wunderkind:
            self.wunder_gimbal.draw(screen)


    def drawAll(self, screen):
        self.draw(screen)
        for child in self.children:
            child.drawAll(screen)

    def drawAllExtra(self, screen):
        self.drawExtra(screen)
        for child in self.children:
            child.drawAllExtra(screen)



    def __str__(self):
        return f"Bone: Length=>{self.length} Angle=>{self.angle}"


def constructBoneFromXMLNode(bone_node):

    bone = Bone()
    bone.length = float(bone_node.attrib["len"])
    bone.angle = float(bone_node.attrib["angle"])
    bone.frame_angles.append(bone.angle)

    
    if "w" in bone_node.attrib.keys():
        bone.other_end = True

    if "color" in bone_node.attrib.keys():
        cs = bone_node.attrib["color"].split("|")
        col = tuple(map(lambda x : int(x), cs))
        bone.color = col

    type_str = bone_node.attrib["type"]
    if type_str == "circle":
        bone.type = BoneType.CIRCLE
    
    for child_node in bone_node:
        child_bone = constructBoneFromXMLNode(child_node)
        child_bone.parent = bone
        bone.children.append(child_bone)

    return bone


class Figure:
    def __init__(self, root):
        self.root = root
        self.root.pos_x1 = 200
        self.root.pos_y1 = 240
        self.root.frame_translations.append((self.root.pos_x1, self.root.pos_x2))
        self.root.updateAll()

    @classmethod
    def fromFile(cls, xml_fname):

        tree = ET.parse(xml_fname)
        root_bone_node  = tree.getroot().find("bone")
        root_bone = constructBoneFromXMLNode(root_bone_node)
        root_bone.wunderkind = True

        return cls(root_bone)
    
    def addFrame(self):
        self.root.addFrame()
    
    def checkPressed(self, mouseCoords):
        #self.root.checkPressedAll(mouseCoords)
        self.root.checkPressed(mouseCoords)
    
    def update(self):
        self.root.updateAll()

    def draw(self, screen):
        self.root.drawAll(screen)
        self.root.drawAllExtra(screen)

