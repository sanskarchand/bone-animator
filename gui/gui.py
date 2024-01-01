from .utils import BitSet
from .const import LINE_GAP, DEBUG_DRAW
import pygame as pg
from enum import IntFlag
from dataclasses import dataclass

RATIO = 1       # rect height to font size ratio


class GUIElem:
    def __init__(self, screen, pos, width, height):
        """
        Properties:
            callback: ref to function object
        """
        self.screen = screen
        self.pos = pos
        self.width = width
        self.height = height
        self.style = GUIStyle()
        
        # TODO: increase no. of callbacks (or add slots, ids, etc.)
        self.callback = None        # a hook for the programmer
        self.callback_args = []     # tuple of references
        self.callback_on = None     # target state, e.g. ElemState.PRESSED    

        # to trigger, the mouse be within the elem's rect
        # at the instant of the state transition
        # NOTE: OR'ing ElemState.HOVER with callback_on wouldn't 
        # work (think about negation)
        self.callback_needs_mouse = False

        # defines which transition triggers the callback
        # i.e. True => triggered on unpressed to pressed,
        #   and the reverse when it's False
        self.callback_positive = True  
        
        # <event callback>
        # connected func; a callback used for signaling mostly
        # e.g.when text changes in an input field
        self.cfunc = None        

        self.state = BitSet()

        self.rect = self.make_rect()

    def make_rect(self):
        return pg.rect.Rect(self.pos[0], self.pos[1], self.width, self.height)
    
    # NOTE: just use @property?
    def set_pos(self, pos):
        self.pos = pos
        self.rect.x, self.rect.y = pos

    def set_callback(self, func, args_tuple):
        """
        Returns self; for method chaining
        NOTE: if there is only one arg, make sure to write the
              tuple like so : (x,) [otherwise, it's just evaluated
              as an expression]
        """
        self.callback = func
        self.callback_args = args_tuple
        return self     
    
    def connect(self, callback):
        self.cfunc = callback
        return self

    def set_style(self, style):
        """
        style: an object of type GUIStyle
        """
        self.style = style
    
    def flip_state(self):
        self.state.flip(ElemState.PRESSED)


    def onclick(self):
        """<to be overridden>"""
        pass

    def draw(self):
        """<to be overridden>"""
        pass

    def update(self, event, mouse_pos):
        """
        The base class only 
        """

        old_state = BitSet(self.state.field)
        cursor_on_me = self.rect.collidepoint(mouse_pos)

        if cursor_on_me:
            self.state.set(ElemState.HOVER)
                
            if event.type == pg.MOUSEBUTTONDOWN:
                self.state.set(ElemState.PRESSED)
                self.state.set(ElemState.FOCUSED)

            elif event.type == pg.MOUSEBUTTONUP:
                # only counts as a click if the elem
                # was previously pressed
                if self.state.test(ElemState.PRESSED):
                    self.state.clear(ElemState.PRESSED)
                    self.onclick()
        else:
            # to cancel an action, simply move the cursor
            # out of the bounding box to safely clear
            # the pressed state
            self.state.clear(ElemState.PRESSED)
            self.state.clear(ElemState.HOVER)

            # if the user clicks outside this elem, it's not in focus anymore
            if event.type == pg.MOUSEBUTTONUP:
                self.state.clear(ElemState.FOCUSED)

        if not self.callback:
            return

        if self.callback_needs_mouse and not cursor_on_me:
            return

        # check for state triggers (for callback)
        target_state = self.callback_on

        # on positive transition
        if self.callback_positive:
            if not old_state.test(target_state) and self.state.test(target_state):
                self.callback(*self.callback_args)
        else:
            if old_state.test(target_state) and not self.state.test(target_state):
                self.callback(*self.callback_args)
            


class ElemState(IntFlag):
    """
    If PRESSED isn't present in a flag bitset,
    it means the element is raised
    """
    NONE = 0x0 
    PRESSED = 0x1       
    HOVER = 0x2 
    FOCUSED = 0x4

# for containers
class Orientation(IntFlag):
    NULL = 0x0
    HORIZONTAL = 0x1
    VERTICAL = 0x2
    

class Color:
    def __init__(self, r=148, g=255, b=147):
        self.r = r
        self.g = g
        self.b = b

    def is_unset(self):
        return (self.r == self.g == self.b ==  None)
    
    @property
    def raw(self):
        return (self.r, self.g, self.b)

    def __repr__(self):
        #return f"<Color>({self.r},{self.g},{self.b})</Color>"
        return f"Color<#{hex(self.r)[2:]}{hex(self.g)[2:]}{hex(self.b)[2:]}>"


    @classmethod
    def new_scaled(cls, scale, color):

        def scale_color(c):
            return int( min(c * scale, 255) )

        r, g, b = list(map(scale_color, (color.r, color.g, color.b)))
        return cls(r, g, b) 
    
    @classmethod
    def from_hex(cls, hex_string):
        if not hex_string:
            return

        if hex_string[0] == '#':
            hex_string = hex_string[1:]

        if len(hex_string) < 6:
            return

        r = int(hex_string[:2], 16)
        g = int(hex_string[2:4], 16)
        b = int(hex_string[4:6], 16)

        return cls(r, g, b)




@dataclass
class GUIStyle:
    bg_color = Color(222, 222, 222)
    bg_hover_color = None           # overrides default lightened color if set
    fg_color = Color(255, 255, 255)
    
    font = 'Envy Code R Regular'    # string - system font name
    font_size = None                # None means auto (acc. to width)
    font_color = Color(0, 0, 0)
    font_bold = False
    font_italic = False

    border_color = None             # use a tuple to specify color
    border_width = None             # use an integer (border thickness)

    def set_border(self, b_col, b_width):
        self.border_color = Color(b_col[0], b_col[1], b_col[2])
        self.border_width = b_width

class Label(GUIElem):
    def __init__(self, screen, pos, width, height):
        """
            width, height are useless for the time being,
            but they may later be used for clipping.
        """
        super().__init__(screen, pos, width, height)
        self.font = self.font = self.make_pygame_font()
        self.style.bg_color = Color(None, None, None)   # no bg
        self.text = ''
    
    # TODO: separate parent class for text-based behaviour
    def set_text(self, text):
        self.text = text 
        self.recalc_height()
        return self         # chaining
    
    def recalc_height(self):
        lines = self.text.split('\n')
        if len(lines) == 1:
            return

        dh = 0
        self.height = 0
        for line in lines: 
            dh += self.style.font_size//2  + LINE_GAP
            self.height += dh

        self.height -= dh

        self.rect = self.make_rect()

    #NOTE: redundant 
    def make_pygame_font(self):
        self.style.font_size = int(RATIO * self.rect.height)
        return pg.font.SysFont(self.style.font,
                        self.style.font_size,
                        self.style.font_bold,
                        self.style.font_italic)

    def draw(self):
        if DEBUG_DRAW:
            pg.draw.rect(self.screen, (0, 0, 255), self.rect, 1)

        # draw a bg, if an actual color is given
        if not self.style.bg_color.is_unset():
            pg.draw.rect(self.screen, self.style.bg_color.raw, self.rect)

        # handle newlines, too
        lines = self.text.split('\n')
        dh = 0

        for line in lines: 
            # NOTE: needn't create a new surf every time
            text_surface = self.font.render(line, False, self.style.font_color.raw)
            self.screen.blit(text_surface, (self.pos[0], self.pos[1] + dh))
            dh += self.style.font_size//2 + LINE_GAP


class TextInput(GUIElem):

    def __init__(self, screen, pos, width, height):
        super().__init__(screen, pos, width, height)
        self.text = ''
        self.cursor_pos = -1
        self.font = self.make_pygame_font()
    
    def set_font(self, font_name, font_bold=False, font_italic=False):
        self.style.font = font_name
        self.style.font_bold = font_bold
        self.style.font_italic = font_italic
        self.font = self.make_pygame_font()

    def make_pygame_font(self):
        self.style.font_size = int(RATIO * self.rect.height)
        return pg.font.SysFont(self.style.font,
                        self.style.font_size,
                        self.style.font_bold,
                        self.style.font_italic)

    def update(self, event, mouse_pos):
        super().update(event, mouse_pos)
        if not self.state.test(ElemState.FOCUSED):
            return
        

        keys = pg.key.get_pressed()

        if event.type == pg.KEYDOWN:

            # alphanumeric input
            if event.key >= ord('a') and event.key <= ord('z'):
                if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
                    self.text += chr(event.key - 32)
                else:
                    self.text += chr(event.key)

            if event.key >= ord('0') and event.key <= ord('9'):
                self.text += chr(event.key)

            if event.key == pg.K_SPACE:
                self.text += ' '
            
            # backspace
            if keys[pg.K_BACKSPACE]:
                self.text = self.text[:-1]
            
            # invoke callback on keydown
            if self.cfunc:
                self.cfunc(self.text)
        
        # 97 to 122, 48 to 57
        # capture keyboard input for copy-paste

        
        
    def draw(self):
        if DEBUG_DRAW:
            pg.draw.rect(self.screen, (48, 48, 48), self.rect)

        # draw bg white
        pg.draw.rect(self.screen, self.style.bg_color.raw, self.rect)

        # draw border rectangle
        pg.draw.rect(self.screen, Color(0, 0, 0).raw, self.rect, 3)
        
        text = self.text
        if self.state.test(ElemState.FOCUSED):
            text += "|"

        text_surface = self.font.render(text, False, self.style.font_color.raw)
        cropped_region = (0, 0, self.rect.width-3, self.rect.height)
        textpos = (self.pos[0] + 3, self.pos[1] + 3)

        self.screen.blit(text_surface, textpos, cropped_region)
        #self.screen.blit(text_surface, textpos)


class Button(GUIElem):
    def __init__(self, screen, pos, width, height):
        super().__init__(screen, pos, width, height)
        
        # trigger callback when button is released
        #   with the cursor within the button
        self.callback_on = ElemState.PRESSED
        self.callback_positive = False
        self.callback_needs_mouse = True
       

    def draw(self):
        color = self.style.bg_color

        if self.state.test(ElemState.HOVER):
            color = Color.new_scaled(1.2, color)
        # darkened color
        if self.state.test(ElemState.PRESSED):
            color = Color.new_scaled(0.8, color)
        
        pg.draw.rect(self.screen, color.raw, self.rect)

        # draw border
        if self.style.border_width:
            pg.draw.rect(self.screen, self.style.border_color.raw,
                    self.rect, self.style.border_width)

        
class TextButton(Button):
    def __init__(self, screen, pos, width, height, text):
        super().__init__(screen, pos, width, height)
        self.text = text
        self.font = self.make_pygame_font()
    
    def set_font(self, font_name, font_bold=False, font_italic=False):
        self.style.font = font_name
        self.style.font_bold = font_bold
        self.style.font_italic = font_italic
        self.font = self.make_pygame_font()

    def make_pygame_font(self):
        self.style.font_size = int(RATIO * self.rect.height)
        return pg.font.SysFont(self.style.font,
                        self.style.font_size,
                        self.style.font_bold,
                        self.style.font_italic)
        

    def draw(self):
        super().draw()
        text_surface = self.font.render(self.text, False, self.style.font_color.raw)

        # center the text
        textpos_x = int( self.pos[0] + (self.rect.width - text_surface.get_rect().width)/2 )
        textpos_y = int( self.pos[1] + (self.rect.height - text_surface.get_rect().height)/2 )

        
        self.screen.blit(text_surface, (textpos_x, textpos_y))

class ImageButton(Button):
    def __init__(self, screen, pos, width, height, image):
        super().__init__(screen, pos, width, height)
        self.image = image


### Dialog boxes
class DialogBox(GUIElem):
    def __init__(self, screen, pos, width, height):
        super().__init__(screen, pos, width, height)
        self.ok_button = None


### Containers
class Container(GUIElem):
    def __init__(self, screen, pos, width, height):
        super().__init__(screen, pos, width, height)
        self.items = []
        self.orientation = Orientation.HORIZONTAL
        self.direction = 1      # 1 for left-to-right, up-to-down. -1 for the opposite
        self.gap = 20
        self.margin = (20, 0)

    def set_orientation(self, ori):
        self.orientation = ori
        return self

    def push_items(self, *items):
        for item in items:
            self.push_item(item)

    def push_item(self, item):
        if self.items:
            last_item = self.items[-1]
            if self.orientation == Orientation.HORIZONTAL:
                new_x = last_item.pos[0] + (self.direction) * (last_item.width + self.gap)
                item.set_pos((new_x, last_item.pos[1]))
            else:
                new_y = last_item.pos[1] + (self.direction) * (last_item.height + self.gap)
                item.set_pos((last_item.pos[0], new_y))
        else:
            pos = self.pos

            if self.direction == -1:
                if self.orientation == Orientation.HORIZONTAL:
                    pos = self.pos[0] - item.width, self.pos[1]
                else:
                    pos = self.pos[0], self.pos[1] - item.height
            
            # we need only apply the margin to the first
            # item, since subsequent items look to  last_item for
            # positioning info
            pos = (self.margin[0] + pos[0], self.margin[1] + pos[1])
            item.set_pos(pos)

        self.items.append(item)

    def pop_item(self):
        return self.items.pop()

    def update(self, event, mouse_pos):
        for item in self.items:
            item.update(event, mouse_pos)

    def draw(self):
        for item in self.items:
            item.draw()

        if DEBUG_DRAW:
            rect = pg.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
            if self.direction == -1:
                if self.orientation == Orientation.HORIZONTAL:
                    rect.x -= rect.width
                else:
                    rect.y -= rect.height

            pg.draw.rect(self.screen, (0, 0, 255), rect, 2)

    

class GUI:

    def __init__(self, screen):
        self.screen = screen
        self.elems = []

    def add_elem(self, elem):
        self.elems.append(elem)

    def make_horizontal_container(self, pos, width, height):
        return (Container(self.screen, pos, width, height)
                .set_orientation(Orientation.HORIZONTAL))
    
    def make_vertical_container(self, pos, width, height):
        return (Container(self.screen, pos, width, height)
                .set_orientation(Orientation.VERTICAL))

    def make_button(self, pos, width, height, callback, callback_args):
        return (Button(self.screen, pos, width, height)
                .set_callback(callback, callback_args))

    def make_text_button(self, pos, width, height, text, callback, callback_args):
        return (TextButton(self.screen, pos, width, height, text)
                .set_callback(callback, callback_args))

    def make_label(self, pos, width, height, text):
        return (Label(self.screen, pos, width, height)
                .set_text(text))

    def make_text_input(self, pos, width, height):
        return TextInput(self.screen, pos, width, height)
        
    def update(self, event, mouse_pos):
        for elem in self.elems:
            elem.update(event, mouse_pos)

    def draw(self):
        for elem in self.elems:
            elem.draw()

