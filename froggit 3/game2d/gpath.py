"""
Auxiliary drawables for 2D game support.

This module provides support for non-rectangular objects such as triangles, polygons,
and paths (e.g. lines with width).  

Author: Walker M. White (wmw2)
Date:   August 1, 2017 (Python 3 version)
"""
# Lower-level kivy modules to support animation
from kivy.graphics import *
from kivy.graphics.instructions import *
from .gobject import GObject


def same_side(p1, p2, a, b):
    """
    Checks whether two points are on the same side of a line segment.
    
    :param p1: A point represented as a 2-element sequence of numbers
    :type p1:  ``list`` or ``tuple``
    
    :param p2: A point represented as a 2-element sequence of numbers
    :type p2:  ``list`` or ``tuple``
    
    :param a: One end of a line segment, represented as a 2-element sequence of numbers
    :type a:  ``list`` or ``tuple``
    
    :param b: Another end of a line segment, represented as a 2-element sequence of numbers
    :type b:  ``list`` or ``tuple``
    
    :return: True if ``p1``, ``p2`` are on the same side of segment ``ba``; False otherwise
    :rtype:  ``bool``
    """
    import numpy as np
    ba  = np.append(np.subtract(b,a),[0])
    cp1 = np.cross(ba,np.subtract(p1,a))
    cp2 = np.cross(ba,np.subtract(p2,a))
    return np.dot(cp1,cp2) >= 0


def in_triangle(p, t):
    """
    Checks whether a point is inside of a triangle
    
    :param p: A point in 2 dimensions
    :type p:  2-element list of ``int`` or ``float``
    
    :param t: A triangle defined by 3 points
    :type t:  6-element list of ``int`` or ``float``
    
    :return: True if ``p`` is in triangle ``t``; False otherwise
    :rtype:  ``bool``
    """
    return (same_side(p, t[0:2], t[2:4], t[4:6]) and
            same_side(p, t[2:4], t[0:2], t[4:6]) and
            same_side(p, t[4:6], t[0:2], t[2:4]))


def is_point_tuple(t,minsize):
    """
    Checks whether a value is an EVEN sequence of numbers.
    
    The number of points tuple must be size greater than or equal to ``minsize``, or the 
    function returns False.  As a point is a pair of numbers, this means the length of
    list ``t`` must be at least **twice** ``minsize``.
    
    :param t: The value to test
    :type t:  any
    
    :param minsize: The minimum number of points in the sequence
    :type minsize:  ``int`` >= 0
    
    :return: True if t is a point sequence (i.e. even sequence of numbers); False otherwise
    :rtype:  ``bool``
    """
    try:
        from functools import reduce
        return len(t) % 2 == 0 and len(t) >= 2*minsize and \
            reduce(lambda x, y: x and y, map(lambda z: type(z) in [int, float], t))
    except:
        return False


#mark -
class GPath(GObject):
    """
    A class representing a sequence of line segments
    
    The path is defined by the ``points`` attribute which is an (even) sequence of 
    alternating x and y values. When drawn in a :class:`GView` object, the line starts 
    from one x-y pair in ``points`` and goes to the next x-y pair.  If ``points`` has 
    length 2n, then the result is n-1 line segments.
    
    The object uses the attribute ``linecolor`` to determine the color of the line and the
    attribute ``linewidth`` to determine the width.  The attribute ``fillcolor`` is unused 
    (even though it is inherited from :class:`GObject`).
    
    The attributes ``width`` and ``height`` are present in this object, but they are now
    read-only.  These values are computed from the list of points.
    
    On the other hand, the attributes ``x`` and ``y`` are used.  By default, these values
    are 0.  However, if they are nonzero, then Python will add them to all of the points
    in the path, shifting the path accordingly.
    """
    
    # MUTABLE PROPERTIES
    @property
    def points(self):
        """
        The sequence of points that make up this line.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be even with length at least 4.
        """
        return self._points
    
    @points.setter
    def points(self,value):
        assert is_point_tuple(value,2),'value %s is not a valid list of points' %  repr(value)
        self._points = tuple(value)
        if self._defined:
            self._reset()
    
    @property
    def linewidth(self):
        """
        The width of this path.
        
        Setting this value to 0 means that the path is invisible.
        
        **Invariant**: Must be an int or float >= 0.
        """
        return self._linewidth
    
    @linewidth.setter
    def linewidth(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        assert value >= 0, 'value %s is negative' % repr(value)
        self._linewidth = value
        if self._defined:
            self._reset()
    
    
    # IMMUTABLE PROPERTIES
    @property
    def width(self):
        """
        The horizontal width of this path. 
        
        The value is the width of the smallest bounding box that contains all of the
        points in the line AND the origin (0,0).
        
        **Invariant**: Must be an int or float > 0.
        """ 
        px = self.points[::2]+(0,0)
        return 2*max(max(px),-min(px))
    
    @property
    def height(self):
        """
        The vertical height of this path. 
        
        The value is the height of the smallest bounding box that contains all of the
        points in the line AND the origin (0,0).
        
        **Invariant**: Must be an int or float > 0.
        """ 
        py = self.points[1::2]+(0,0)
        return 2*max(max(py),-min(py))
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new sequence of line segments.
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to create a 
        path from (0,0) to (2,3) with width 2, use the constructor call
            
            GPath(points=[0,0,2,3],linewidth=2)
        
        This class supports the same keywords as :class:`GObject`, though some of them 
        are unused, as the ``width`` and ``height`` attributes are now immutable. The 
        primary keywords for this class are ``points``, ``linecolor``, and ``linewidth``.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.linewidth = keywords['linewidth'] if 'linewidth' in keywords else 1.0
        self.points = keywords['points'] if 'points' in keywords else (0,0,10,10)
        if not 'linecolor' in keywords:
            keywords['linecolor'] = (1,1,1,1)
        GObject.__init__(self,**keywords)
        self._reset()
        self._defined = True
    
    
    # PUBLIC METHODS
    def contains(self,point):
        """
        Checks whether this shape contains the point
        
        This method always returns `False` as a ``GPath`` has no interior.
        
        :param point: the point to check
        :type point: :class:`Point2`` or a pair of numbers
        
        :return: True if the shape contains this point
        :rtype:  ``bool``
        """
        return False
    
    def near(self,point):
        """
        Checks whether this path is near the given point
        
        To determine if (x,y) is near the path, we compute the minimum distances
        from (x,y) to the path.  If this distance is less than e-6, we return True.
        
        :param point: the point to check
        :type point: :class:`Point2`` or a pair of numbers
        
        :return: True if this path is near the give point; False otherwise.
        :rtype:  ``bool``
        """
        if isinstance(point,Point2):
            point = (point.x,point.y)
        assert is_point_tuple(point,1),'value %s is not a valid point' %  repr(point)
        x = point[0]
        y = point[1]
        
        size = len(self.points)/2
        epsilon = 1e-6
        for ii in range(size-1):
            p = self.points[2*ii  :2*ii+2]
            q = self.points[2*ii+2:2*ii+4]
            if p == q:
                test = np.sqrt((q[0]-x)*(q[0]-x)+(q[1]-y)*(q[1]-y)) < epsilon
            else:
                num = abs((q[0]-p[0])*x-(q[1]-p[1])*y+q[0]*p[1]-p[0]*q[1])
                den = np.sqrt((q[0]-p[0])*(q[0]-p[0])+(q[1]-p[1])*(q[1]-p[1]))
                test = num/den
            if test:
                return True
        
        return self.contains(point)
    
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache
        """
        GObject._reset(self)
        if not self._linecolor is None:
            self._cache.add(self._linecolor)
            line = Line(points=self.points,cap='round',joint='round',width=self.linewidth)
            self._cache.add(line)
        self._cache.add(PopMatrix())


#mark -
class GTriangle(GPath):
    """
    A class representing a solid triangle.
    
    The triangle is defined as a sequence of three point. Just as with the `GPath` class
    (which is the parent of this class), it has an attribute `point` which represents
    this points as an even-length sequence of ints or floats.
    
    The interior (fill) color of this triangle is `fillcolor`, while `linecolor`
    is the color of the border.  If `linewidth` is set to 0, then the border is 
    not visible.
    
    As with `GPath`, the attributes `x` and `y` may be used to shift the triangle 
    position. By default, these values are 0.  However, if they are nonzero, then Python 
    will add them to the triangle vertices.  Similarly, the attributes `width` and 
    `height` are immutable, and are computed directly from the points
    """
    
    # MUTABLE PROPERTIES
    @property
    def points(self):
        """
        The sequence of vertices that make up this trianle.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be exactly 6.
        """
        return self._points
    
    @points.setter
    def points(self,value):
        assert is_point_tuple(value,3),'value %s is not a valid list of points' %  repr(value)
        assert len(value) == 6, 'value %s does not have the right length'  %  repr(value)
        self._points = tuple(value)
        if self._defined:
            self._reset()
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new solid triangle.
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to create a 
        red triangle with vertices (0,0), (2,3), and (0,4), use the constructor call::
            
            GTriangle(points=[0,0,2,3,0,4],fillcolor=colormodel.RED)
        
        As with :class:`GPath` the ``width`` and ``height`` attributes of this class are 
        both immutable.  They are computed from the list of points.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.linewidth = keywords['linewidth'] if 'linewidth' in keywords else 0.0
        self.points = keywords['points'] if 'points' in keywords else (-100,-58,0,116,100,-58)
        GObject.__init__(self,**keywords)
        self._reset()
        self._defined = True
    
    
    # PUBLIC METHODS
    def contains(self,point):
        """
        Checks whether this shape contains the point
        
        By default, this method just checks the bounding box of the shape.
        
        **Warning**: Using this method on a rotated object may slow down your framerate.
        
        :param point: the point to check
        :type point: :class:`Point2`` or a pair of numbers
        
        :return: True if the shape contains this point
        :rtype:  ``bool``
        """
        if isinstance(point,Point2):
            point = (point.x,point.y)
        assert is_point_tuple(point,1), "%s is not a valid point" % repr(point)
        
        return in_triangle(points,self._points)
    
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache
        """
        GObject._reset(self)
        
        vertices = ()
        for x in range(3):
            # Need to tack on degenerate texture coords
            vertices += self.points[2*x:2*x+2]+(0,0)
        mesh = Mesh(vertices=vertices, indices=range(3), mode='triangle_strip')
        self._cache.add(self._fillcolor)
        self._cache.add(mesh)
        
        if self.linewidth > 0:
            line = Line(points=self.points,joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


#mark -
class GPolygon(GPath):
    """
    A class representing a solid polygon.  
    
    The polygon is a triangle fan from the center of the polyon to the vertices in the
    attribute ``points``. The center of the polygon is always the point (0,0), unless 
    you reassign the attributes ``x`` and ``y``.  However, as with :class:`GPath`, if you
    assign the attributes ``x`` and ``y``, then Python will shift all of the vertices by 
    that same amount. Hence the polygon vertices must be defined as triangle fan centered 
    at the origin.
    
    The interior (fill) color of this polygon is ``fillcolor``, while ``linecolor``
    is the color of the border.  If ``linewidth`` is set to 0, then the border is 
    not visible.
    
    The polygon may also be textured by specifying a source image. The texture coordinates 
    of each vertex will be relative to the size of the image.  For example, if the image 
    is 64x64, then the quad polygon (-32,-32,-32,32,32,32,32,-32) will be a rectangle 
    equal to the image.  You can adjust the size of the source image with the attributes
    `source_width` and `source_height`. If the polygon is larger than the image, then the 
    texture will repeat.
    
    As with :class:`GPath`, the attributes ``width`` and ``height`` are immutable, and 
    are computed directly from the points
    """
    
    # MUTABLE PROPERTIES
    @property
    def points(self):
        """
        The sequence of points that make up this polygon.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be even with length at least 6.
        """
        return self._points
    
    @points.setter
    def points(self,value):
        assert is_point_tuple(value,3),'value %s is not a valid list of points' %  repr(value)
        self._points = tuple(value)
        if self._defined:
            self._reset()
    
    @property
    def source(self):
        """
        The source image for texturing this polygon
        
        **Invariant**. Must be a string refering to a valid file.
        """
        return self._source

    @source.setter
    def source(self,value):
        from .app import GameApp
        assert value is None or GameApp.is_image(value), 'value %s is not an image file' % repr(value)
        self._source = value
        if self._defined:
            self._reset()
    
    @property
    def source_width(self):
        """
        The width to scale the source image.
        
        The texture coordinates of each vertex will be relative to the size of the image.  
        For example, if the image is 64x64, then the polygon (-32,-32,-32,32,32,32,32,-32) 
        will be a rectangle equal to the image.
        
        This attribute allows you to resize the image for these texture coordinates. So
        if the image is 512x64, setting this value to 64 will be as if the image was 
        originally 64x64. If this value is None, the Python will use the normal width
        of the image file
        
        **Invariant**. Must be a number (int or float) > 0 or None.
        """
        return self._source_width
    
    @source_width.setter
    def source_width(self,value):
        assert value is None or type(value) in [int,float], 'value %s is not a valid width' % repr(value)
        self._source_width = None
        if self._defined:
            self._reset()
    
    @property
    def source_height(self):
        """
        The height to scale the source image.
        
        The texture coordinates of each vertex will be relative to the size of the image.  
        For example, if the image is 64x64, then the polygon (-32,-32,-32,32,32,32,32,-32) 
        will be a rectangle equal to the image.
        
        This attribute allows you to resize the image for these texture coordinates. So
        if the image is 64x512, setting this value to 64 will be as if the image was 
        originally 64x64. If this value is None, the Python will use the normal width
        of the image file
        
        **Invariant**. Must be a number (int or float) > 0 or None.
        """
        return self._source_width
    
    @source_height.setter
    def source_height(self,value):
        assert value is None or _is_num(value), 'value %s is not a valid width' % repr(value)
        self._source_height = None
        if self._defined:
            self._reset()
    
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new solid polyon
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to create a 
        hexagon, use the constructor call::
            
            GPolygon(points=[87,50,0,100,-87,50,-87,-50,0,-100,87,-50])
        
        As with :class:`GPath` the ``width`` and ``height`` attributes of this class are 
        both immutable.  They are computed from the list of points.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        self._defined = False
        self.linewidth = keywords['linewidth'] if 'linewidth' in keywords else 0.0
        self.points = keywords['points'] if 'points' in keywords else (-100,-58,0,116,100,-58)
        self.source = keywords['source'] if 'source' in keywords else None
        self.source_width  = keywords['source_width']  if 'source_width'  in keywords else None
        self.source_height = keywords['source_height'] if 'source_height' in keywords else None
        GObject.__init__(self,**keywords)
        self._reset()
        self._defined = True
    
    
    # PUBLIC METHODS
    def contains(self,point):
        """
        Checks whether this shape contains the point
        
        By default, this method just checks the bounding box of the shape.
        
        **Warning**: Using this method on a rotated object may slow down your framerate.
        
        :param point: the point to check
        :type point: :class:`Point2`` or a pair of numbers
        
        :return: True if the shape contains this point
        :rtype:  ``bool``
        """
        if isinstance(point,Point2):
            point = (point.x,point.y)
        assert is_point_tuple(point,1), "%s is not a valid point" % repr(point)
        
        found = False
        for i in xrange(4,len(self._points),2):
            t = (0,0)+self.points[i-4:i]
            found = found or in_triangle(point,t)
        
        return found
    
    
    # HIDDEN METHODS
    def _make_mesh(self):
        """
        Creates the mesh for this polygon
        """
        size = len(self.points)/2
        try:
            texture = Image(source=self.source).texture
            texture.wrap = 'repeat'
            tw = float(texture.width)  if self.source_width is None else self.source_width
            th = float(texture.height) if self.source_height is None else self.source_height
            
            # Centroid at 0, with texture centered
            verts = (0,0,0.5,0.5) 
            
            # Create the fan.
            for x in range(size):
                pt = self.points[2*x:2*x+2]
                self._verts += pt+(pt[0]/tw+0.5,pt[1]/th+0.5)
            
            # Come back to the beginning
            pt = self.points[0:2]
            verts += pt+(pt[0]/tw+0.5,pt[1]/th+0.5)
            self._mesh = Mesh(vertices=verts, indices=range(size+2), mode='triangle_fan', texture=texture)
        except BaseException as e:
            # Make all texture coordinates degnerate
            verts = (0,0,0,0) 
            for x in range(size):
                verts += self.points[2*x:2*x+2]+(0,0)
            verts += self.points[0:2]+(0,0)
            self._mesh = Mesh(vertices=verts, indices=range(size+2), mode='triangle_fan')
    
    def _reset(self):
        """
        Resets the drawing cache
        """
        GObject._reset(self)
        self._make_mesh()
        
        self._cache.add(self._fillcolor)
        self._cache.add(self._mesh)
        
        if self.linewidth > 0:
            line = Line(points=self.points,joint='miter',close=True,width=self.linewidth)
            self._cache.add(self._linecolor)
            self._cache.add(line)
        
        self._cache.add(PopMatrix())


