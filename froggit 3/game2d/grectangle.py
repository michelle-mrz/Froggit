"""
The most important drawables for 2D game support.

This module provides support for all of the drawables with rectangular bounding boxes
(this includes circles and ellipses).  This is the primary module that you will need
to draw shapes.

Author: Walker M. White (wmw2)
Date:   August 1, 2017 (Python 3 version)
"""
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.uix.label import Label
from kivy.uix.image import Image
from .gobject import GObject
from .app import GameApp

class GRectangle(GObject):
    """
    A class representing a (potentially) solid rectangle.
    
    As with :clas:`GObject`, the attributes x and y refer to the center of the rectangle. 
    This is so that when you rotate the rectangle, it spins about the center.
    
    The interior (fill) color of this rectangle is `fillcolor`.  If this value is None,
    then the rectangle is not solid.  The color  `linecolor` is the color of the border.
    
    The only new property for this class is ``linewidth``, which controls the width of
    the border around the rectangle.  For all other properties, see the documentation
    for :class:`GObject`."""
    
    # MUTABLE PROPERTIES 
    @property
    def linewidth(self):
        """
        The width of the exterior line of this shape.
        
        Setting this to 0 means that the rectangle has no border.
        
        **invariant**: Value must be an ``int`` or ``float`` >= 0.
        """
        return self._linewidth
    
    @linewidth.setter
    def linewidth(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        assert value >= 0, '%s is negative' % repr(value)
        self._linewidth = value
        if self._defined:
            self._reset()
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new solid rectangle
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to create a 
        red square centered at (0,0), use the constructor call::
            
            GRectangle(x=0,y=0,width=10,height=10,fillcolor='red')
        
        This class supports the all same keywords as :class:`GObject` plus the additional
        keyword ``linewidth``.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.linewidth = keywords['linewidth'] if 'linewidth' in keywords else 0.0
        # Always delay the call to parent class, to avoid reset
        GObject.__init__(self,**keywords)
        self._reset()
        self._defined = True
    
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache
        """
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if not self._fillcolor is None:
            fill = Rectangle(pos=(x,y), size=(self.width, self.height))
            self._cache.add(self._fillcolor)
            self._cache.add(fill)
        
        if not self._linecolor is None and self.linewidth > 0:
            line = Line(rectangle=(x,y,self.width,self.height),joint='miter',
                        close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


#mark -
class GEllipse(GRectangle):
    """
    A class representing a solid ellipse.
    
    The ellipse is the largest one that can be drawn inside of a rectangle whose bottom 
    center is at (x,y), with the given width and height.  The interior (fill) color of 
    this ellipse is ``fillcolor``. If this value is None, then the ellipse is not solid.  
    The color  `linecolor` is the color of the border.
    
    This class has exactly the same properties as :class:`GRectangle`.  See the 
    documentation of that class and :class:`GObject` for a complete list of attributes.
    """
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new solid ellipse
        
        To use the constructor for this class, you should provide it with a list of
        keyword arguments that initialize various attributes. For example, to create a 
        red circle centered at (0,0), use the constructor call::
            
            GEllipse(x=0,y=0,width=10,height=10,fillcolor='red')
        
        This class supports the all same keywords as :class:`GRectangle`.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        GRectangle.__init__(self,**keywords)
    
    
    # PUBLIC METHODS
    def contains(self,point):
        """
        Checks whether this shape contains the point
        
        This method is better than simple rectangle inclusion.  It checks that the point 
        is within the proper radius as well.
        
        **Warning**: Using this method on a rotated object may slow down your framerate.
        
        :param point: the point to check
        :type point: :class:`GPoint`` or a pair of numbers
        """
        if isinstance(point,GPoint):
            point = (point.x,point.y)
        assert is_num_tuple(point,2), "%s is not a valid point" % repr(point)
        
        rx = self.width/2.0
        ry = self.height/2.0
        if self._rotate.angle == 0.0:
            dx = (point[0]-self.x)*(point[0]-self.x)/(rx*rx)
            dy = (point[1]-self.y)*(point[1]-self.y)/(ry*ry)
        else:
            p = self.matrix.inverse()._transform(point[0],point[1])
            dx = p[0]*p[0]/(rx*rx)
            dy = p[1]*p[1]/(ry*ry)
        
        return (dx+dy) <= 1.0
    
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if not self._fillcolor is None:
            fill = Ellipse(pos=(x,y), size=(self.width,self.height))
            self._cache.add(self._fillcolor)
            self._cache.add(fill)
        
        if not self._linecolor is None and self.linewidth > 0:
            line = Line(ellipse=(x,y,self.width,self.height),close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


#mark -
class GImage(GRectangle):
    """
    A class representing a rectangular image.
    
    The image is given by a JPEG, PNG, or GIF file whose name is stored in the attribute 
    `source`.  Image files should be stored in the **Images** directory so that Kivy can 
    find them without the complete path name.
    
    This class acts much like is parent :class:`GRectangle` and shares all of the same 
    properties. As with that class, you can add a border to the rectangle if you want, 
    using the attribute ``linewidth``.  The border will be rectangular, not matter the
    image transparency.
    
    If the attributes ``width`` and ``height`` do not agree with the actual size of the 
    image, the image is scaled to fit.Furthermore, if you define ``fillcolor``, this 
    object will tint your image by the given color.`
    
    If the image supports transparency, then this object can be used to represent irregular 
    shapes.  However, the :meth:`contains` method still treats this shape as a  rectangle.
    """
    
    # MUTABLE PROPERTIES
    @property
    def source(self):
        """
        The source file for this image.
        
        **invariant**. Value be a string refering to a valid file.
        """
        return self._source

    @source.setter
    def source(self,value):
        assert value is None or GameApp.is_image(value), '%s is not an image file' % repr(value)
        self._source = value
        if self._defined:
            self._reset()
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new rectangular image.
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to load the 
        image ``beach-ball.png``, use the constructor::
            
            GImage(x=0,y=0,width=10,height=10,source='beach-ball.png')
        
        This class supports the all same keywords as :class:`GRectangle`; the only new 
        keyword is ``source``.  See the documentation of :class:`GRectangle` and 
        :class:`GObject` for the other supported keywords.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.source = keywords['source'] if 'source' in keywords else None
        self._texture = None
        GRectangle.__init__(self,**keywords)
        self._defined = True
    
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        GObject._reset(self)
        
        self._texture = GameApp.load_texture(self.source)
        if not self._texture is None and (self.width == 0 or self.height == 0):
                self.width  = self._texture.width
                self.height = self._texture.height
        
        x = -self.width/2.0
        y = -self.height/2.0
        fill = Rectangle(pos=(x,y), size=(self.width, self.height),texture=self._texture)
        if not self._fillcolor is None:
            self._cache.add(self._fillcolor)
        else:
            self._cache.add(Color(1,1,1))
        self._cache.add(fill)
        
        if not self._linecolor is None and self.linewidth > 0:
            line = Line(rectangle=(x,y,self.width,self.height),joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


#mark -
class GLabel(GRectangle):
    """
    A class representing an (uneditable) text label
    
    This object is exactly like a GRectangle, except that it has the possibility of
    containing some text.
    
    The attribute `text` defines the text content of this label.  Uses of the escape 
    character `'\\n'` will result in a label that spans multiple lines.  As with any
    `GRectangle`, the background color of this rectangle is `fillcolor`, while 
    `linecolor` is the color of the text.
    
    The text itself is aligned within this rectangle according to the attributes `halign` 
    and `valign`.  See the documentation of these attributes for how alignment works.  
    There are also attributes to change the point size, font style, and font name of the 
    text. The `width` and `height` of this label will grow to ensure that the text will 
    fit in the rectangle, no matter the font or point size.
    
    To change the font, you need a .ttf (TrueType Font) file in the Fonts folder; refer 
    to the font by filename, including the .ttf. If you give no name, it will use the 
    default Kivy font.  The `bold` attribute only works for the default Kivy font; for 
    other fonts you will need the .ttf file for the bold version of that font.  See the
    provided `ComicSans.ttf` and `ComicSansBold.ttf` for an example."""
    
    # MUTABLE PROPERTIES
    @property
    def font_size(self):
        """
        The size of the text font in points.
        
        **Invariant**: Must be a positive number (int or float)"""
        return self._fsize
    
    @font_size.setter
    def font_size(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        self._fsize = value
        self._label.font_size = value
        self._label.texture_update()
    
    @property
    def font_name(self):
        """
        The file name for the .ttf file to use as a font
        
        **Invariant**: Must be a string referring to a .ttf file in folder Fonts"""
        return self._label.font_name
    
    @font_name.setter
    def font_name(self,value):
        from .app import GameApp
        assert GameApp.is_font(value), 'value %s is not a font name' % repr(value)
        self._label.font_name = value
        self._label.texture_update()
    
    @property
    def bold(self):
        """
        A boolean indicating whether or not the text should be bold.
        
        This value only works on the default Kivy font.  It does not work on custom
        .ttf files.  In that case, you need the bold version of the .ttf file.  See 
        `ComicSans.ttf` and `ComicSansBold.ttf` for an example.
        
        **Invariant**: Must be a boolean"""
        return self._label.bold

    @bold.setter
    def bold(self,value):
        assert type(value) == bool, repr(value)+' is not a bool'
        self._label.bold = value
        self._label.texture_update()

    @property
    def text(self):
        """
        The text for this label.
        
        The text in the label is displayed as a single line, or broken up into multiple 
        lines in the presence of the escape character `'\\n'`. The `width` and `height` of 
        this label will grow to ensure that the text will fit in the rectangle.
        
        **Invariant**: Must be a string"""
        return self._label.text
    
    @text.setter
    def text(self,value):
        assert type(value) == str, 'value %s is not a string' % repr(value)
        self._label.text = value
        self._label.texture_update()
    
    @property
    def halign(self):
        """
        The horizontal alignment for this label.
        The text is horizontally anchored inside of the label rectangle at either the 
        left, the right or the center.  This means that as the size of the label 
        increases, the text will still stay rooted at that anchor.  By default, the
        text is centered.
        
        *This attribute has no effect unless the label rectangle is larger than the
        text it contains*.  This attribute only applies to the position of the text
        inside of the box.  It cannot be used to center the text on screen.
        
        **Invariant**: Must be one of 'left', 'right', or 'center'"""
        return self._halign
    
    @halign.setter
    def halign(self,value):
        assert value in ('left','right','center'), 'value %s is not a valid horizontal alignment' % repr(value)
        self._halign = value
        self._label.halign = value
        if self._defined:
            self._reset()
    
    @property
    def valign(self):
        """Vertical alignment for this label.
        
        The text is vertically anchored inside of the label rectangle at either the top, 
        the bottom or the middle.  This means that as the size of the label increases, 
        the text will still stay rooted at that anchor.  By default, the text is in
        the middle.
        
        *This attribute has no effect unless the label rectangle is larger than the
        text it contains*.  This attribute only applies to the position of the text
        inside of the box.  It cannot be used to center the text on screen.
        
        **Invariant**: Must be one of 'top', 'bottom', or 'middle'"""
        return self._valign
    
    @valign.setter
    def valign(self,value):
        assert value in ('top','middle','bottom'), 'value %s is not a valid vertical alignment' % repr(value)
        self._valign = value
        self._label.valign = value
        if self._defined:
            self._reset()
    
    
    # REDEFINED PROPERTIES
    @property
    def x(self):
        """
        The horizontal coordinate of the object center.
        
        **Invariant**: Must be an int or float."""
        return self._trans.x
    
    @x.setter
    def x(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        self._trans.x = float(value)
        self._mtrue = False
        self._hanchor = 'center'
        self._ha = value
    
    @property
    def y(self):
        """
        The vertical coordinate of the object center..
        
        **Invariant**: Must be an int or float."""
        return self._trans.y
    
    @y.setter
    def y(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        self._trans.y = float(value)
        self._mtrue = False
        self._vanchor = 'center'
        self._hv = value
    
    @property
    def left(self):
        """
        The left edge of this shape.
        
        The value depends on the current angle of rotation. If rotation is 0, it is
        `x-width/2`.  Otherwise, it is the left-most value of the bounding box.
        
        Changing this value will shift the center of the object so that the left
        edge matches the new value.
        
        **Warning**: Accessing this value on a rotated object may slow down your framerate.
        
        **Invariant**: Must be an int or float.
        """
        if self._rotate.angle == 0.0:
            return self.x-self.width/2.0
        
        p0 = self.matrix._transform(self.x-self.width/2.0, self.y-self.height/2.0)[0]
        p1 = self.matrix._transform(self.x+self.width/2.0, self.y-self.height/2.0)[0]
        p2 = self.matrix._transform(self.x+self.width/2.0, self.y+self.height/2.0)[0]
        p3 = self.matrix._transform(self.x-self.width/2.0, self.y+self.height/2.0)[0]
        return min(p0,p1,p2,p3)
    
    @left.setter
    def left(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        diff = value-self.left
        self.x += diff
        self._hanchor = 'left'
        self._ha = value
    
    @property
    def right(self):
        """
        The right edge of this shape.
        
        The value depends on the current angle of rotation. If rotation is 0, it is
        `x+width/2`.  Otherwise, it is the right-most value of the bounding box.
        
        Changing this value will shift the center of the object so that the right
        edge matches the new value.
        
        **Warning**: Accessing this value on a rotated object may slow down your framerate.
        
        **Invariant**: Must be an int or float.
        """
        if self._rotate.angle == 0.0:
            return self.x+self.width/2.0
        
        p0 = self.matrix._transform(self.x-self.width/2.0, self.y-self.height/2.0)[0]
        p1 = self.matrix._transform(self.x+self.width/2.0, self.y-self.height/2.0)[0]
        p2 = self.matrix._transform(self.x+self.width/2.0, self.y+self.height/2.0)[0]
        p3 = self.matrix._transform(self.x-self.width/2.0, self.y+self.height/2.0)[0]
        return max(p0,p1,p2,p3)
    
    @right.setter
    def right(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        diff = value-self.right
        self.x += diff
        self._hanchor = 'right'
        self._ha = value
    
    @property
    def top(self):
        """
        The vertical coordinate of the top edge.
        
        The value depends on the current angle of rotation. If rotation is 0, it is
        `y+height/2`.  Otherwise, it is the top-most value of the bounding box.
        
        Changing this value will shift the center of the object so that the top
        edge matches the new value.
        
        **Warning**: Accessing this value on a rotated object may slow down your framerate.
        
        **Invariant**: Must be an int or float.
        """
        if self._rotate.angle == 0.0:
            return self.y+self.height/2.0
        
        p0 = self.matrix._transform(self.x-self.width/2.0, self.y-self.height/2.0)[1]
        p1 = self.matrix._transform(self.x+self.width/2.0, self.y-self.height/2.0)[1]
        p2 = self.matrix._transform(self.x+self.width/2.0, self.y+self.height/2.0)[1]
        p3 = self.matrix._transform(self.x-self.width/2.0, self.y+self.height/2.0)[1]
        return max(p0,p1,p2,p3)
    
    @top.setter
    def top(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        diff = value-self.top
        self.y += diff
        self._vanchor = 'top'
        self._hv = value
    
    @property
    def bottom(self):
        """
        The vertical coordinate of the bottom edge.
        
        The value depends on the current angle of rotation. If rotation is 0, it is
        `y-height/2`.  Otherwise, it is the bottom-most value of the bounding box.
        
        Changing this value will shift the center of the object so that the bottom
        edge matches the new value.
        
        **Warning**: Accessing this value on a rotated object may slow down your framerate.
        **Invariant**: Must be an int or float.
        """
        if self._rotate.angle == 0.0:
            return self.y-self.height/2.0
        
        p0 = self.matrix._transform(self.x-self.width/2.0, self.y-self.height/2.0)[1]
        p1 = self.matrix._transform(self.x+self.width/2.0, self.y-self.height/2.0)[1]
        p2 = self.matrix._transform(self.x+self.width/2.0, self.y+self.height/2.0)[1]
        p3 = self.matrix._transform(self.x-self.width/2.0, self.y+self.height/2.0)[1]
        return min(p0,p1,p2,p3)
    
    
    @bottom.setter
    def bottom(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        diff = value-self.bottom
        self.y += diff
        self._vanchor = 'bottom'
        self._hv = value
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new text label.
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes.  For example, to create a 
        label containing the word 'Hello', use the constructor call::
            
            GLabel(text='Hello')
        
        This class supports the all same keywords as :class:`GRectangle`, as well as 
        additional attributes for the text properties (e.g. font size and name).
        """
        self._defined = False
        self._hanchor = 'center'
        self._vanchor = 'center'
        
        sanitized = {}
        excludes  = ['linewidth','linecolor','fillcolor','halign','valign','left','bottom']
        for key in keywords:
            if not key in excludes:
                sanitized[key] = keywords[key]
        
        self._label = Label(**sanitized)
        self._label.size_hint = (None,None)
        
        self.linewidth = keywords['linewidth'] if 'linewidth' in keywords else 0.0
        self.halign = keywords['halign'] if 'halign' in keywords else 'center'
        self.valign = keywords['valign'] if 'valign' in keywords else 'middle'
        
        GObject.__init__(self,**keywords)
        if not self.linecolor:
            self.linecolor = (0,0,0,1)
        self._reset()
        self._defined = True
        self._label.bind(texture_size=self._callback)
    
    def __str__(self):
        """
        :return: A readable string representation of this object.
        :rtype:  ``str``
        """
        if self.name is None:
            s = '['
        else:
            s = '[name=%s,' % self.name
        return '%s,text=%s,center=(%s,%s),angle=%s]' \
                % (s,repr(self.text),repr(self.x),repr(self.y),repr(self.angle))
    
    # HIDDEN METHODS
    def _callback(self,instance=None,value=None):
        """
        A workaround to deal with parameter requirements for callbacks
        """
        if self._defined:
            self._reset()
    
    def _reset(self):
        """
        Resets the drawing cache.
        """
        # Set up the label at the center.
        self._label.size = self._label.texture_size
        self._label.center = (0,0)
        if self.linecolor:
            self._label.color = self.linecolor
        
        # Resize the outside if necessary
        self._defined = False
        self._width  = max(self.width, self._label.width)
        self._height = max(self.height,self._label.height)
        self._defined = True
        
        # Reset the absolute anchor
        if self._hanchor == 'left':
            self._trans.x = self._ha+self.width/2.0
        elif self._hanchor == 'right':
            self._trans.x = self._ha-self.width/2.0
        
        # Reset the absolute anchor
        if self._vanchor == 'top':
            self._trans.y = self._hv-self.height/2.0
        elif self._vanchor == 'bottom':
            self._trans.y = self._hv+self.height/2.0
        
        # Reset the label anchor.
        if self.halign == 'left':
            self._label.x = -self.width/2.0
        elif self.halign == 'right':
            self._label.right = self.width/2.0
        
        # Reset the label anchor.
        if self.valign == 'top':
            self._label.top = self.height/2.0
        elif self.valign == 'bottom':
            self._label.bottom = -self.height/2.0
        
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        if self.fillcolor:
            fill = Rectangle(pos=(x,y), size=(self.width,self.height))
            self._cache.add(self._fillcolor)
            self._cache.add(fill)
        
        self._cache.add(self._label.canvas)
        
        if self._linewidth > 0:
            line = Line(rectangle=(x,y,self.width,self.height),joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())
