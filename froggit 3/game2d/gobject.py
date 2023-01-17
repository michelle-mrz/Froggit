"""
The base classes for 2D game support.

This module provides the base drawable class, as well as simple scene graph support.
These classes will not work unless you adhere to proper subclassing practices.


Author: Walker M. White (wmw2)
Date:   November 1, 2020
"""
from kivy.graphics import *
from kivy.graphics.instructions import *
from introcs.geom import Point2, Matrix


def is_color(c):
    """
    Checks whether a value represents a color.

    As with Turtles, colors may be introcs objects or strings.  They may also be
    sequences of 3 or 4 elements.  In the case of the latter, the elements of the
    sequence must all be in the range 0..1.

    :return: True if c represents a color
    :rtype:  ``bool``

    :param c: The value to test
    :type c:  any
    """
    import introcs
    if type(c) in [introcs.RGB, introcs.HSV]:
        return True

    if type(c) in [tuple, list] and 3 <= len(c) <= 4:
        from functools import reduce
        return reduce(lambda x, y: x and y, map(lambda z: type(z) in [int, float] and 0 <= z <= 1, c))

    return type(c) == str and (introcs.is_tkcolor(c) or introcs.is_webcolor(c))


def is_num_tuple(t,size):
    """
    Checks whether a value is a sequence of numbers.

    If the sequence is not of the given size, it also returns False.

    :return: True if t is a sequence of numbers; False otherwise
    :rtype:  ``bool``

    :param t: The value to test
    :type t:  any

    :param size: The size of the sequence
    :type size:  ``int`` >= 0
    """
    try:
        from functools import reduce
        return len(t) == size and reduce(lambda x, y: x and y, map(lambda z: type(z) in [int, float], t))
    except:
        return False


def is_gobject_list(g):
    """
    Checks whether a value is a a sequence of :class:`GObject`

    :return: True if g is a sequence of GObjects
    :rtype:  ``bool``

    :param g: The value to test
    :type g:  any
    """
    try:
        from functools import reduce
        return len(g) >= 0 and reduce(lambda x, y: x and y, map(lambda z: isinstance(z,GObject), g))
    except:
        return False


#mark -

class GObject(object):
    """
    An class representing a basic graphics object.

    A graphics object is an object to draw on the screen.  To draw it, you will need
    an instance of :class:`GView`, which is passed to the :meth:`draw` method.

    You should never make a `GObject` directly.  Instead, you should use one of the
    subclasses: :class:`GRectangle`, :class:`GEllipse`, :class:`GImage`, :class:`GLabel`,
    :class:`GTriangle`, :class:`GPolygon`, or :class:`GPath`.
    """

    # MUTABLE PROPERTIES
    @property
    def x(self):
        """
        The horizontal coordinate of the object center.

        **invariant**: Value must be an ``int`` or ``float``
        """
        return self._trans.x

    @x.setter
    def x(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._trans.x = float(value)
        self._mtrue = False

    @property
    def y(self):
        """
        The vertical coordinate of the object center.

        **invariant**: Value must be an ``int`` or ``float``
        """
        return self._trans.y

    @y.setter
    def y(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        self._trans.y = float(value)
        self._mtrue = False

    @property
    def width(self):
        """
        The horizontal width of this shape.

        Positive values go to the right.

        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._width

    @width.setter
    def width(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        assert value > 0, '%s is not positive' % repr(value)
        self._width = float(value)
        if self._defined:
            self._reset()

    @property
    def height(self):
        """
        The vertical height of this shape.

        Positive values go up.

        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        return self._height

    @height.setter
    def height(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        assert value > 0, '%s is not positive' % repr(value)
        self._height = float(value)
        if self._defined:
            self._reset()

    @property
    def hitbox(self):
        """
        The hitbox for this object.

        The hitbox is a rectangle that need not agree with the bounding rectangle
        of this object. For example, images are have transparencies on their edges,
        which means tha the visible part of the image is smaller than the image file
        as a hole.  The hitbox attribute reflects this difference, so that we can
        have accurate collisions.

        If hitbox is None, then the normal bounding box (given by x, y, width, height)
        is used for collisions.  Otherwise, hitbox is an 4-element list of *offsets*.
        Each value is the amount to pull the hitbox in towards the center of the object.
        For example, a hitbox of (1,2,3,4) says to shift the left edge of the hitbox 1
        pixel to the right, the top edge 2 pixels down, the right edge 3 pixels to the
        left, and the bottom edge 4 pixels up.

        **Invariant**: Value is either ``None`` or a 4-element tuple of numbers.
        """
        return self._hitbox

    @hitbox.setter
    def hitbox(self,value):
        if value is None:
            self._hitbox = None
            return

        try:
            size = len(value)
        except:
            size = 0
        assert size == 4, '%s is not a tuple or list of size 4' % repr(value)
        assert all(map(lambda x : type(x) in [int,float], value)), '%s has non-numerical elements' % repr(value)
        self._hitbox = tuple(value)

    @property
    def scale(self):
        """
        The scaling factor of this shape.

        The scale is a fast way to cause a shape to grow or shrink in size. Essentially,
        the object will multiple the width and height by the scale.  So a scale less than
        1 will shrink the object, while a scale greater than 1 will enlarge the object.

        The scale may either be a single number, or a pair of two numbers.  If it is
        a single number, it will scale the width and height by the same amount. If it is
        a pair, it will scale the width by the first value, and the height by the second.

        **invariant**: Value must be either a number (``int`` or ``float``) or a pair of numbers.
        """
        return (self._scale.x,self._scale.y)

    @scale.setter
    def scale(self,value):
        # Do some checking here
        assert type(value) in [int,float] or is_num_tuple(value,2), \
                '%s is not a valid scaling factor' % repr(value)
        if type(value) in [int,float]:
            self._scale.x = float(value)
            self._scale.y = float(value)
        else:
            self._scale.x = float(value[0])
            self._scale.y = float(value[1])
        self._mtrue = False

    @property
    def angle(self):
        """
        The angle of rotation about the center.

        The angle is measured in degrees (not radians) counter-clockwise.

        **invariant**: Value must be an ``int`` or ``float``
        """
        return self._rotate.angle

    @angle.setter
    def angle(self,value):
        import numpy as np
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        diff = np.allclose([self._rotate.angle],[value])
        self._rotate.angle = float(value)
        if not diff:
            self._mtrue = False

    @property
    def linecolor(self):
        """
        The object line color

        This is the border color of the shape.  If there no value (e.g. the linecolor
        is ``None``), this shape will have no border.

        The default representation of color in GObject is a 4-element list of floats
        between 0 and 1 (representing r, g, b, and a).  As with the Turtle, you may also
        assign color an `RGB` or `HSV` object from `introcs`, or a string with a valid
        color name. If you chose either of these alternate representations (a string or
        an object from `introcs`), Python will automatically convert the result into
        a 4-element list.

        **invariant**: Value must be ``None`` or a 4-element list of floats between 0 and 1.
        """
        return None if self._linecolor is None else self._linecolor.rgba

    @linecolor.setter
    def linecolor(self,value):
        import introcs
        assert value is None or is_color(value), '%s is not a valid color' % repr(value)
        if type(value) in [tuple, list] and len(value) == 3:
            value = list(value)+[1.0]
        elif type(value) in [introcs.RGB, introcs.HSV]:
            value = value.glColor()
        elif type(value) == str:
            if value[0] == '#':
                value = introcs.RGB.CreateWebColor(value).glColor()
            else:
                value = introcs.RGB.CreateName(value).glColor()

        self._linecolor = None if value is None else Color(value[0],value[1],value[2],value[3])
        if self._defined:
            self._reset()

    @property
    def fillcolor(self):
        """
        The object fill color

        This value is used to color the backgrounds or, in the case of solid shapes,
        the shape interior. If there no value (e.g. the fillcolor is ``None``), this
        shape will have no interior.

        The default representation of color in GObject is a 4-element list of floats
        between 0 and 1 (representing r, g, b, and a).  As with the Turtle, you may also
        assign color an `RGB` or `HSV` object from `introcs`, or a string with a valid
        color name. If you chose either of these alternate representations (a string or
        an object from `introcs`), Python will automatically convert the result into
        a 4-element list.

        **invariant**: Value must be ``None`` or a 4-element list of floats between 0 and 1.
        """
        return None if self._fillcolor is None else self._fillcolor.rgba

    @fillcolor.setter
    def fillcolor(self,value):
        import introcs
        assert value is None or is_color(value), '%s is not a valid color' % repr(value)
        if type(value) in [tuple, list] and len(value) == 3:
            value = list(value)+[1.0]
        elif type(value) in [introcs.RGB, introcs.HSV]:
            value = value.glColor()
        elif type(value) == str:
            if value[0] == '#':
                value = introcs.RGB.CreateWebColor(value).glColor()
            else:
                value = introcs.RGB.CreateName(value).glColor()

        self._fillcolor = None if value is None else Color(value[0],value[1],value[2],value[3])
        if self._defined:
            self._reset()

    @property
    def name(self):
        """
        The name of this object.

        This value is for debugging purposes only.  If you name an object, the name
        will appear when you convert the object to a string.  This will allow you to
        tell which object is which in your watches.

        **invariant**: Value must be a ``str`` or ``None``
        """
        return self._name

    @name.setter
    def name(self,value):
        assert value is None or type(value) == str, '%s is not a valid name' % repr(value)
        self._name = value

    # DERIVED PROPERTIES
    @property
    def left(self):
        """
        The left edge of this shape.

        The value depends on the current angle of rotation. If rotation is 0, it is
        ``x-width/2``.  Otherwise, it is the left-most value of the bounding box.

        Changing this value will shift the center of the object so that the left
        edge matches the new value.

        **Warning**: Accessing this value on a rotated object may slow down your framerate.

        **invariant**: Value must be an ``int`` or ``float``.
        """
        # Optimize for 90 degree turns
        if (self._rotate.angle % 360) == 0.0:
            return self.x-self.width/2.0+self._hitbox[0]
        elif (self._rotate.angle % 360) == 180:
            return self.x-self.width/2.0+self._hitbox[2]
        elif (self._rotate.angle % 360) == 90.0:
            return self.x-self.height/2.0+self._hitbox[3]
        elif (self._rotate.angle % 360) == 270:
            return self.x-self.height/2.0+self._hitbox[1]

        p0 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0], -self.height/2.0+self._hitbox[3]))[0]
        p1 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2], -self.height/2.0+self._hitbox[3]))[0]
        p2 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2],  self.height/2.0+self._hitbox[1]))[0]
        p3 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0],  self.height/2.0+self._hitbox[1]))[0]
        return min(p0,p1,p2,p3)

    @left.setter
    def left(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        diff = value-self.left
        self.x += diff

    @property
    def right(self):
        """
        The right edge of this shape.

        The value depends on the current angle of rotation. If rotation is 0, it is
        ``x+width/2``.  Otherwise, it is the right-most value of the bounding box.

        Changing this value will shift the center of the object so that the right
        edge matches the new value.

        **Warning**: Accessing this value on a rotated object may slow down your framerate.

        **invariant**: Value must be an ``int`` or ``float``.
        """
        # Optimize for 90 degree turns
        if (self._rotate.angle % 360) == 0.0:
            return self.x+self.width/2.0-self._hitbox[2]
        elif (self._rotate.angle % 360) == 180:
            return self.x+self.width/2.0-self._hitbox[0]
        elif (self._rotate.angle % 360) == 90.0:
            return self.x+self.height/2.0-self._hitbox[1]
        elif (self._rotate.angle % 360) == 270:
            return self.x+self.height/2.0-self._hitbox[3]

        p0 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0], -self.height/2.0+self._hitbox[3]))[0]
        p1 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2], -self.height/2.0+self._hitbox[3]))[0]
        p2 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2],  self.height/2.0+self._hitbox[1]))[0]
        p3 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0],  self.height/2.0+self._hitbox[1]))[0]
        return max(p0,p1,p2,p3)

    @right.setter
    def right(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        diff = value-self.right
        self.x += diff

    @property
    def top(self):
        """
        The vertical coordinate of the top edge.

        The value depends on the current angle of rotation. If rotation is 0, it is
        ``y+height/2``.  Otherwise, it is the top-most value of the bounding box.

        Changing this value will shift the center of the object so that the top
        edge matches the new value.

        **Warning**: Accessing this value on a rotated object may slow down your framerate.

        **invariant**: Value must be an ``int`` or ``float``.
        """
        # Optimize for 90 degree turns
        if (self._rotate.angle % 360) == 0.0:
            return self.y+self.height/2.0-self._hitbox[1]
        elif (self._rotate.angle % 360) == 180:
            return self.y+self.height/2.0-self._hitbox[3]
        elif (self._rotate.angle % 360) == 90.0:
            return self.y+self.width/2.0-self._hitbox[0]
        elif (self._rotate.angle % 360) == 270:
            return self.y+self.width/2.0-self._hitbox[2]

        p0 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0], -self.height/2.0+self._hitbox[3]))[1]
        p1 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2], -self.height/2.0+self._hitbox[3]))[1]
        p2 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2],  self.height/2.0+self._hitbox[1]))[1]
        p3 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0],  self.height/2.0+self._hitbox[1]))[1]
        return max(p0,p1,p2,p3)

    @top.setter
    def top(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        diff = value-self.top
        self.y += diff

    @property
    def bottom(self):
        """
        The vertical coordinate of the bottom edge.

        The value depends on the current angle of rotation. If rotation is 0, it is
        ``y-height/2``.  Otherwise, it is the bottom-most value of the bounding box.

        Changing this value will shift the center of the object so that the bottom
        edge matches the new value.

        **Warning**: Accessing this value on a rotated object may slow down your framerate.

        **invariant**: Value must be an ``int`` or ``float``.
        """
        # Optimize for 90 degree turns
        if (self._rotate.angle % 360) == 0.0:
            return self.y-self.height/2.0+self._hitbox[3]
        elif (self._rotate.angle % 360) == 180:
            return self.y-self.height/2.0+self._hitbox[1]
        elif (self._rotate.angle % 360) == 90.0:
            return self.y-self.width/2.0+self._hitbox[2]
        elif (self._rotate.angle % 360) == 270:
            return self.y-self.width/2.0+self._hitbox[0]

        p0 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0], -self.height/2.0+self._hitbox[3]))[1]
        p1 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2], -self.height/2.0+self._hitbox[3]))[1]
        p2 = tuple(self.matrix._transform( self.width/2.0+self._hitbox[2],  self.height/2.0+self._hitbox[1]))[1]
        p3 = tuple(self.matrix._transform(-self.width/2.0+self._hitbox[0],  self.height/2.0+self._hitbox[1]))[1]
        return min(p0,p1,p2,p3)


    @bottom.setter
    def bottom(self,value):
        assert type(value) in [int,float], '%s is not a number' % repr(value)
        diff = value-self.bottom
        self.y += diff


    # IMMUTABLE PROPERTIES
    @property
    def matrix(self):
        """
        The transformation matrix for this object

        This value is constructed dynamically as needed.  It should only be used
        internally in this package

        **invariant**: Either a :class:`Matrix` or ``None``
        """
        if not self._mtrue or self._matrix is None:
            self._build_matrix()
        return self._matrix

    @property
    def inverse(self):
        """
        The inverse transformation matrix for this object

        This value is constructed dynamically as needed.  It should only be used
        internally in this package

        **invariant**: Either a :class:`Matrix` or ``None``
        """
        if not self._mtrue or self._matrix is None:
            self._build_matrix()
        return self._invrse


    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new GObject to be drawn.

        To use the constructor for this class, you should provide it with a list of
        keyword arguments that initialize various attributes.  For example, to initialize
        the x position and the fill color, use the constructor call::

            GObject(x=2,fillcolor='red')

        You do not need to provide the keywords as a dictionary. The ** in the parameter
        `keywords` does that automatically.

        Any attribute of this class may be used as a keyword. The argument must satisfy
        the invariants of that attribute. See the list of attributes of this class for
        more information.

        :param keywords: dictionary of keyword arguments
        :type keywords:  keys are attribute names
        """
        # Set the properties.
        self._defined = False

        # Create the Kivy transforms for position and size
        self._mtrue  = False
        self._trans  = Translate(0,0,0)
        self._rotate = Rotate(angle=0,axis=(0,0,1))
        self._scale  = Scale(1,1,1)

        # Now update these with the keywords; size first
        try:
            self._width  = keywords['width']  if 'width'  in keywords else 0
            self._height = keywords['height'] if 'height' in keywords else 0
        except:
            pass

        # Now the hitbox offsets
        self.hitbox =  keywords['hitbox']  if 'hitbox'  in keywords else (0,0,0,0)

        # Then angle
        if 'angle' in keywords:
            self.angle = keywords['angle']

        # Finally, (relative) position
        if 'x' in keywords:
            self.x = keywords['x']
        elif 'left' in keywords:
            self.left = keywords['left']
        elif 'right' in keywords:
            self.right = keywords['right']

        if 'y' in keywords:
            self.y = keywords['y']
        elif 'bottom' in keywords:
            self.bottom = keywords['bottom']
        elif 'top' in keywords:
            self.top = keywords['top']

        # Top it off with color
        self.fillcolor = keywords['fillcolor'] if 'fillcolor' in keywords else None
        self.linecolor = keywords['linecolor'] if 'linecolor' in keywords else None

        # Add a name for debugging
        self.name = keywords['name'] if 'name' in keywords else None

    def __str__(self):
        """
        :return: A readable string representation of this object.
        :rtype:  ``str``
        """
        if self.name is None:
            s = '['
        else:
            s = '[name=%s,' % self.name
        return '%s,center=(%s,%s),width=%s,height=%s,angle=%s]' \
                % (s,repr(self.x),repr(self.y),repr(self.height),repr(self.width),repr(self.angle))

    def __repr__(self):
        """
        :return: An unambiguous string representation of this object.
        :rtype:  ``str``
        """
        return str(self.__class__)+str(self)


    # PUBLIC METHODS
    def collides(self,obj):
        """
        Checks whether this object collides with another.

        This collision method takes hitboxes into account

        :param obj: the object to check for collision
        :type obj: :class:`GObject`

        :return: True if the shape collides with object
        :rtype:  ``bool``
        """
        assert isinstance(obj,GObject), '%s is not an instance of GObject' % repr(obj)

        # Get the hitboxes
        h1 = (0,0,0,0) if self._hitbox is None else self._hitbox
        h2 = (0,0,0,0) if obj._hitbox is None else obj._hitbox

        # Optimize for 90 degree turns
        if (self.angle % 360) in [0,90,180,270] and (obj.angle % 360) in [0,90,180,270]:
            (l0,t0,r0,b0) = obj._bbox()
            (l1,t1,r1,b1) = self._bbox()
            isx = l1 <= l0 <= r1 or l0 <= l1 <= r0
            isy = b1 <= b0 <= t1 or b0 <= b1 <= t0
            return isx and isy

        comp = obj.matrix*self.matrix.inverse()
        w = obj.width/2.0
        h = obj.height/2.0
        p0 = tuple(comp._transform(-w+h2[0], h-h2[1]))
        p1 = tuple(comp._transform( w-h2[2], h-h2[1]))
        p2 = tuple(comp._transform( w-h2[2],-h+h2[3]))
        p3 = tuple(comp._transform(-w+h2[0],-h+h2[3]))

        sides = ((p0,p1),(p1,p2),(p2,p3),(p3,p0))
        l1 = -self.width/2.0  + h1[0]
        r1 =  self.width/2.0  - h1[2]
        t1 =  self.height/2.0 - h1[1]
        b1 = -self.height/2.0 + h1[3]
        for s in sides:
            l0 = min(s[0][0],s[1][0])
            r0 = max(s[0][0],s[1][0])
            b0 = min(s[0][1],s[1][1])
            t0 = max(s[0][1],s[1][1])
            isx = l1 <= l0 <= r1 or l0 <= l1 <= r0
            isy = b1 <= b0 <= t1 or b0 <= b1 <= t0
            if isx and isy:
                return True

        return False

    def contains(self,point):
        """
        Checks whether this shape contains the point

        By default, this method just checks the bounding box of the shape.

        **Warning**: Using this method on a rotated object may slow down your framerate.

        :param point: the point to check
        :type point: :class:`Point2` or a pair of numbers

        :return: True if the shape contains this point
        :rtype:  ``bool``
        """
        if isinstance(point,Point2):
            point = (point.x,point.y)
        assert is_num_tuple(point,2), "%s is not a valid point" % repr(point)

        # Optimize for 90 degree turns
        if (self._rotate.angle % 360) in [0,90,180,270]:
            (l,t,r,b) = self._bbox()
            return l <= point[0] <= r and b <= point[1] <= t

        # Transform this to the right space.
        point = tuple(self.matrix.inverse()._transform(point[0],point[1]))
        w = self.width/2.0
        h = self.height/2.0
        isx = - w + self._hitbox[0] <= point[0] <= w - self._hitbox[2]
        isy = - h + self._hitbox[3] <= point[1] <= h - self._hitbox[1]
        return isx and isy

    def transform(self,point):
        """
        Transforms the point to the local coordinate system

        This method is important for mouse selection.  It helps you understand where
        in the shape the selection takes place.  In the case of objects with children,
        like :class:`GScene`, this method is necessary to properly use the contains method
        on the children.

        :param point: the point to transform
        :type point: :class:`Point2` or a pair of numbers

        :return: The point transformed to local coordinate system
        :rtype:  :class:`Point2`
        """
        if isinstance(point,Point2):
            return self.inverse.transform(point)
        else:
            assert is_num_tuple(point,2), "%s is not a valid point" % repr(point)
            p = self.inverse._transform(point[0],point[2])
            return Point2(p[0],p[1])

    def draw(self, view):
        """
        Draws this shape in the provided view.

        Ideally, the view should be the one provided by :class:`GameApp`.

        :param view: view to draw to
        :type view:  :class:`GView`
        """
        try:
            view.draw(self._cache)
        except:
            raise IOError('Cannot draw %s since it was not initialized properly' % repr(self))

    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        self._cache = InstructionGroup()
        self._cache.add(PushMatrix())
        self._cache.add(self._trans)
        self._cache.add(self._rotate)
        self._cache.add(self._scale)

    def _build_matrix(self):
        """
        Builds the transform matrices after a settings change.
        """
        self._matrix = Matrix()
        self._matrix.scale(self._scale.x,self._scale.y)
        self._matrix.rotate(self._rotate.angle)
        self._matrix.translate(self._trans.x,self._trans.y)
        self._invrse = Matrix()
        self._invrse.translate(-self._trans.x,-self._trans.y)
        self._invrse.rotate(-self._rotate.angle)
        self._invrse.scale(1.0/self._scale.x,1.0/self._scale.y)
        self._mtrue = True

    def _bbox(self):
        """
        Computes the bounding box of this rotated object

        The bounding box is returned as a tuple (l,t,r,b). This function allows for
        fast(er) collisions when the object is rotated in 90 degree increments.

        :return: The bounding box for the shape
        :rtype:  ``tuple`` of four ``float`` values
        """
        oangle = self.angle % 360
        hit = (0,0,0,0) if self._hitbox is None else self._hitbox
        w = self.width/2
        h = self.height/2
        if oangle == 0:
            l = self.x + hit[0] - w
            r = self.x - hit[2] + w
            t = self.y - hit[1] + h
            b = self.y + hit[3] - h
        elif oangle == 90:
            t = self.y + hit[2] - w
            b = self.y - hit[0] + w
            r = self.x - hit[3] + h
            l = self.x + hit[1] - h
        elif oangle == 180:
            l = self.x + hit[2] - w
            r = self.x - hit[0] + w
            t = self.y - hit[3] + h
            b = self.y + hit[1] - h
        elif oangle == 270:
            t = self.y + hit[0] - w
            b = self.y - hit[2] + w
            r = self.x - hit[1] + h
            l = self.x + hit[3] - h
        else:
            comp = self.matrix
            w = self.width/2.0
            h = self.height/2.0
            p0 = tuple(comp._transform(-w+hit[0], h-hit[1]))
            p1 = tuple(comp._transform( w-hit[2], h-hit[1]))
            p2 = tuple(comp._transform( w-hit[2],-h+hit[3]))
            p3 = tuple(comp._transform(-w+hit[0],-h+hit[3]))

            l = min(p0[0],p1[0],p2[0],p3[0])
            r = max(p0[0],p1[0],p2[0],p3[0])
            b = min(p0[1],p1[1],p2[1],p3[1])
            t = max(p0[1],p1[1],p2[1],p3[1])

        return (l,t,r,b)


#mark -

class GScene(GObject):
    """
    A class representing a node in a scene graph.

    A scene graph node is just a collection of :class:`GObject` objects.  By placing
    them in the scene graph node, you can rotate and translate them all at once. Scene
    graphs are a sophisticated concept that allow you to do advanced animation.

    As ``GScene`` is a subclass of :class:`GObject` you can nest scene graph nodes inside
    of other scene graph nodes.  The result is a tree structure.

    The attributes ``width`` and ``height`` are present in this object, but they are now
    read-only.  These values are computed from the list of objects stored in the scene.

    All objects stored in a ``GScene`` are drawn as if the point (x,y) is the origin.
    """

    # MUTABLE PROPERTIES
    @property
    def children(self):
        """
        The list of objects stored in this scene.

        The objects are drawn as if (x,y) is the origin.  Therefore, changing the
        attributes `x` and `y` will shift all of the children on the screen.

        **invariant**: Value must be a list or tuple of :class:`GObject` (possibly empty)
        """
        return tuple(self._children)

    @children.setter
    def children(self,value):
        assert is_gobject_list(value), '%s is not a list of valid objects' % repr(value)
        self._children = list(value)
        if self._defined:
            self._reset()


    # IMMUTABLE PROPERTIES
    @property
    def width(self):
        """
        The horizontal width of this shape.

        The value is the width of the smallest bounding box that contains all of the
        objects in this scene (and the center)

        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        max = 0
        for x in self.children:
            w = x.x+x.width/2.0
            if w > max:
                max = w
        return max*2

    @property
    def height(self):
        """
        The vertical height of this path.

        The value is the height of the smallest bounding box that contains all of the
        objects in this scene (and the center)

        **invariant**: Value must be an ``int`` or ``float`` > 0
        """
        max = 0
        for x in self.children:
            h = x.y+x.height/2.0
            if h > max:
                max = h
        return max*2


    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new scene graph node.

        To use the constructor for this class, you should provide it with a list of
        keyword arguments that initialize various attributes. For example, to create a
        scene with shapes rect, tri, and circ, call the constructor::

            GScene(children=[rect,tri,circ])

        This class supports the same keywords as :class:`GObject`, though some of them
        are unused, as the `width` and `height` attributes are now immutable.

        :param keywords: dictionary of keyword arguments
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.children = keywords['children'] if 'children' in keywords else []
        GObject.__init__(self,**keywords)
        self._reset()
        self._defined = True


    # PUBLIC METHODS
    def select(self,point):
        """
        Selects the child selected by the given point.

        This function recursively descends the scene graph.  It returns the first child
        it finds that contains ``point``.  If that child is also a ``GScene``, it
        recursively calls this method.  If not child contains this point, it returns
        either this object, or ``None`` if the point is completely out of bounds.

        **Warning**: Using this method on a rotated object may slow down your framerate.

        :param point: the point to check
        :type point: :class:`Point2`` or a pair of numbers
        """
        if not self.contains(point):
            return None

        for child in self._children:
            result = None
            if isinstance(child,GScene):
                result = child.select(point)
            elif child.contains(point):
                result = child
            if not child is None:
                return child

        return None


    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache
        """
        GObject._reset(self)
        for x in self.children:
            self._cache.add(x._cache)
        self._cache.add(PopMatrix())
