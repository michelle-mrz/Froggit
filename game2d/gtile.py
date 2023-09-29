"""
A module to support image tiling.

A tile is an image that is repeated multiple times horizontally or vertically.  It is
useful for making things like terrain or highways.  Aside from the repeated textures,
this is very similar to GImage.

Author: Walker M. White (wmw2)
Date:   November 1, 2020
"""
from kivy.graphics import *
from kivy.graphics.instructions import *
from .grectangle import GRectangle, GObject
from .app import GameApp


class GTile(GObject):
    """
    An class representing a tiles image
    
    Normally, ``GImage`` objects scale the image to fit within the given width 
    and height.  A tileable image never scales implicitly (though you can scale
    **explicitly** with the ``scale`` attribute).  Instead it repeats the image
    to fill in all of the remaining space.  This is ideal for terrain and other
    background features
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
    
    # IMMUTABLE PROPERTIES
    @property
    def rows(self):
        """
        The number of times this image appears vertically
        
        This value is a float, as sometimes only a portion of the image is drawn.
        """
        if self._texture is None:
            return 0
        return self.height/self._texture.height
    
    @property
    def columns(self):
        """
        The number of times this image appears horizontally
        
        This value is a float, as sometimes only a portion of the image is drawn.
        """
        if self._texture is None:
            return 0
        return self.width/self._texture.width
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates a new tielable image.
        
        To use the constructor for this class, you should provide it with a list of 
        keyword arguments that initialize various attributes. For example, to load the 
        image ``beach-ball.png``, use the constructor::
            
            GTile(x=0,y=0,width=10,height=10,source='beach-ball.png')
        
        This class supports the all same keywords as :class:`GImage`.  However, the
        attributes `width` and `height` are **required** (so that the object knows how
        much space to fill).  Leaving out these values will cause a `ValueError`.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names, including 'width' and 'height'
        """
        self._defined = False
        self.source = keywords['source'] if 'source' in keywords else None
        if not 'width' in keywords:
            raise ValueError("The 'width' argument must be specified.")
        if not 'height' in keywords:
            raise ValueError("The 'height' argument must be specified.")
        self._texture = None
        GRectangle.__init__(self,**keywords)
        self._defined = True
    
    # HIDDEN METHODS
    def _reset(self):
        """
        Resets the drawing cache.
        """
        GObject._reset(self)
        x = -self.width/2.0
        y = -self.height/2.0
        
        self._texture = GameApp.load_texture(self.source)
        if not self._texture is None and self.width == 0:
            self.width  = self._texture.width
        if not self._texture is None and self.height == 0:
            self.height = self._texture.height
        
        grid_x = self._texture.width
        grid_y = self._texture.height
        size_x = int(self.width//grid_x)
        size_y = int(self.height//grid_y)
        rem_x = self.width-grid_x*size_x
        rem_y = self.height-grid_y*size_y
        
        rng_x = size_x+1 if rem_x > 0 else size_x
        rng_y = size_y+1 if rem_y > 0 else size_y
        
        vert = []
        indx = []
        pos = 0
        for ii in range(rng_x):
            for jj in range(rng_y):
                ni = 1 if ii < size_x else rem_x/grid_x
                nj = 1 if jj < size_y else rem_y/grid_y
                vert.extend([x+ii*grid_x,      y+jj*grid_y,         0, 1])
                vert.extend([x+(ii+ni)*grid_x, y+jj*grid_y,        ni, 1])
                vert.extend([x+(ii+ni)*grid_x, y+(jj+nj)*grid_y,   ni, 1-nj])
                vert.extend([x+ii*grid_x,      y+(jj+nj)*grid_y,    0, 1-nj])
                indx.extend([pos,pos+1,pos+2,pos+2,pos+3,pos])
                pos += 4
        
        mesh = Mesh(vertices=vert, indices=indx,mode='triangles',texture=self._texture)
        if not self._fillcolor is None:
            self._cache.add(self._fillcolor)
        else:
            self._cache.add(Color(1,1,1))
        self._cache.add(mesh)
        
        self._cache.add(PopMatrix())