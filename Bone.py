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
            print("SELECTED!")
            self.selected = True
            self.color = self.color_selected
            self.mouse_prev = mousePos


            
    def deselect(self):
        self.selected = False
        self.color = self.color_normal

    def update(self):

        if self.selected:

            ## update our bone
            cur_mouse = pg.mouse.get_pos()
            dx = cur_mouse[0] - self.bone.pos_x1
            dy = cur_mouse[1] - self.bone.pos_y1

            if (dx != 0 and dy != 0):
                angle = math.atan2(-dy, dx)
                self.bone.angle = angle
                self.bone.calcPropagatedAngle()
                self.bone.update()

        ### update gimbal's rendering from bone pos
        self.pos_x = self.bone.pos_x2
        self.pos_y = self.bone.pos_y2
        self.rect = pg.Rect(self.pos_x -self.rad, self.pos_y - self.rad, 2*self.rad, 2*self.rad)
        

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

        self.bone_pos = (bone.pos_x1, bone.pos_y1)
    


    def update(self):
        if self.selected:
            cur_mouse = pg.mouse.get_pos() 
            if self.bone.figure.position != cur_mouse:
                self.bone.figure.set_position(cur_mouse)


        self.pos_x = self.bone.pos_x1
        self.pos_y = self.bone.pos_y1
        self.rect = pg.Rect(self.pos_x -self.rad, self.pos_y - self.rad, 2*self.rad, 2*self.rad)


            

class Bone:

    def __init__(self, figure, length, angle, wunder=True, b_type=BoneType.LINE):
        self.figure = figure
        self.type = b_type
        self.length = length

        self.angle = angle   # relative angle, or own angle
        self.acc_angle = 0

        self.abs_angle = 0   # absolute angle: total angle accumulated along path from root

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

    def calcPropagatedAngle(self):
        ang = 0
        par  = self.parent
        while par:
            ang += par.angle
            if par.other_end:
                break
            par = par.parent
        
        self.acc_angle = ang


    def update(self):
        
        # for root bone, set position first
        if self.wunderkind:
            self.pos_x1, self.pos_y1 = self.figure.position
        
        ## non-moving bone starts at same pos as parent
        elif self.other_end:
            self.pos_x1 = self.parent.pos_x1
            self.pos_y1 = self.parent.pos_y1

        ## all other normal bones start at end of parent
        else:

            self.pos_x1 = self.parent.pos_x2
            self.pos_y1 = self.parent.pos_y2

        
        if not self.other_end:
            self.angle -= self.acc_angle

        ang = math.radians(self.angle)
        self.pos_x2 = self.pos_x1 + math.cos(ang) * self.length
        self.pos_y2 = self.pos_y1 - math.sin(ang) * self.length

        
        for child in self.children:
            child.update()
        
       

    def checkPressed(self, mousePos):
         self.gimbal.checkPressed(mousePos)
         if self.wunderkind:
            self.wunder_gimbal.checkPressed(mousePos)
    
    def unselectGimbals(self):
        self.gimbal.deselect()
        if self.wunderkind:
            self.wunder_gimbal.deselect()
    
    def drawGimbals(self, screen):
        self.gimbal.draw(screen)
        if self.wunderkind:
            self.wunder_gimbal.draw(screen)


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


        for child in self.children:
            child.draw(screen)


        
    
    def get_flat_hierarchy(self, mut_list):
        for child in self.children:
            mut_list.append(child)
            child.get_flat_hierarchy(mut_list)



    def __str__(self):
        return f"Bone: Length=>{self.length} Angle=>{self.angle}"


def constructBoneFromXMLNode(fig, bone_node):
    
    bone_len = float(bone_node.attrib["len"])
    bone_angle = float(bone_node.attrib["angle"])
    type_str = bone_node.attrib["type"]
    type_map = {
        "circle": BoneType.CIRCLE
    }
    bone_type = type_map.get(type_str, BoneType.LINE)

    bone = Bone(fig, bone_len, bone_angle, b_type=bone_type)
    

    ## set other_end and color
    # TODO: add check to ensure this can only be direct children
    ##  of the root node / wunderkind bone
    if "w" in bone_node.attrib.keys():
        bone.other_end = True

    if "color" in bone_node.attrib.keys():
        cs = bone_node.attrib["color"].split("|")
        col = tuple(map(lambda x : int(x), cs))
        bone.color = col

    
    for child_node in bone_node:
        child_bone = constructBoneFromXMLNode(fig, child_node)
        child_bone.parent = bone
        bone.children.append(child_bone)

    return bone


class Figure:
    def __init__(self):
        self.position = (200, 240)
        self.root = None

    def init_root(self, root):
        self.root = root
        self.root.wunderkind = True
        self.root.update()

        hier = [self.root]
        self.root.get_flat_hierarchy(hier)
        self.flat_bones = hier

        ### get linear bone list for colliderect checks
    

        
    def set_position(self, pos):
        self.position = pos
        self.root.update()

    @classmethod
    def fromFile(cls, xml_fname):
        figure = cls()

        tree = ET.parse(xml_fname)
        root_bone_node  = tree.getroot().find("bone")
        root_bone = constructBoneFromXMLNode(figure, root_bone_node)

        figure.init_root(root_bone)

        return figure 

    
    def addFrame(self):
        self.root.addFrame()
    
    def checkPressed(self, mouseCoords):
        for bone in self.flat_bones:
            bone.checkPressed(mouseCoords)
    
    
    def unselectGimbals(self):
        for bone in self.flat_bones:
            bone.unselectGimbals()


    def update(self):
        """Updates gimbals only at first """
        self.root.wunder_gimbal.update()
        for bone in self.flat_bones:
            bone.gimbal.update()


    def draw(self, screen):
        self.root.draw(screen)
        self.root.drawGimbals(screen)


