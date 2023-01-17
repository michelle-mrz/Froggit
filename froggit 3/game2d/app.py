"""
The primary class for 2D game support.

 To implement a game, you subclass this class and override the three methods ``start``,
 ``update`` and ``draw``.

Author: Walker M. White (wmw2)
Date:   August 1, 2017 (Python 3 version)
"""
# Basic Kivy Modules
import kivy
import kivy.app

# Lower-level kivy modules to support animation
from kivy.config import Config
from kivy.clock  import Clock
from kivy.core.window import Window
from kivy.logger import Logger

import traceback
import os.path
import json
import sys

# Pull off the band aid
import numpy


class GameApp(kivy.app.App):
    """
    A controller class for a simple game application.
    
    This is the primary class for creating a game.  To implement a game, you subclass
    this class and override three methods.  The three methods are as follows:
    
    :meth:`start`: This method initializes the game state, defining all of the game 
    attributes.  This method is like __init__ except that you should not override that 
    method.  Overriding __init__ will break your game. Hence we have provided build as 
    an alternative.
    
    :meth:`update`: This method updates the game state at the start of every animation
    frame.  Any code that moves objects or processes user input (keyboard or mouse)
    goes in this method.
    
    :meth:`draw`: This method draws all of the objects to the screen.  The only 
    thing you should have in this method are calls to ``self.view.draw()``.
    """
    # Class attribute for tracking textures (to reduce memory footprint)
    TEXTURE_CACHE = {}
    
    
    # MUTABLE ATTRIBUTES
    @property
    def fps(self):
        """
        The number of frames-per-second to animate
        
        By default this value is 60 FPS. However, we cannot guarantee that the FPS is 
        achievable.  If you are having performance stuttering, you might want to drop
        this value to 30 FPS instead.
        
        **Invariant**: Must be an int or float > 0.
        """
        return self._fps
    
    @fps.setter
    def fps(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        assert value > 0, 'value %s is not positive' % repr(value)
        Clock.unschedule(self._refresh)
        self._fps = value
        Clock.schedule_interval(self._refresh,1.0/self._fps)
    
    @property
    def width(self):
        """
        The window width
        
        **Invariant**: Must be an int or float > 0.
        """
        return self._gwidth
    
    @width.setter
    def width(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        assert value > 0, 'value %s is not positive' % repr(value)
        self._gwidth = value
        Window.size = (round(self._gwidth), round(self._gheight))
    
    @property
    def height(self):
        """
        The window height
        
        **Invariant**: Must be an int or float > 0.
        """
        return self._gheight
    
    @height.setter
    def height(self,value):
        assert type(value) in [int,float], 'value %s is not a number' % repr(value)
        assert value > 0, 'value %s is not positive' % repr(value)
        self._gheight = value
        Window.size = (round(self._gwidth), round(self._gheight))
    
    
    # IMMUTABLE PROPERTIES
    @property
    def view(self):
        """
        The game view.
        
        Use the `draw` method  in this attribute to display any :class:`GObject` instance 
        on the screen.  See the class :class:`GView` for more information.
        
        **Invariant**: Must be instance of :class:`GView`.
        """
        return self._view
    
    @property
    def input(self):
        """
        The game input handler.
        
        Use this attribute to get information about the mouse and keyboard.  See the
        class :class:`GInput` for more information.
        
        **Invariant**: Must be instance of :class:`GInput`
        """
        return self._input
    
    # CLASS METHODS
    @classmethod
    def is_image(cls,name):
        """
        Checks if ``name`` refers to an image file
    
        The method searches the **Images** folder for the given file name.
    
        :param name: The file name
        :type name:  ``str``
    
        :return: True if ``name`` refers to an image file; False otherwise
        :rtype:  ``bool``
        """
        if type(name) != str:
            return False
    
        return os.path.exists(cls.images+'/'+name)
    
    @classmethod
    def is_font(cls,name):
        """
        Checks if ``name`` refers to a font file
        
        The method searches the **Fonts** folder for the given file name.
        
        :param name: The file name
        :type name:  ``str``
        
        :return: True if ``name`` refers to a font file; False otherwise
        :rtype:  ``bool``
        """
        if type(name) != str:
            return False
        
        return os.path.exists(cls.fonts+'/'+name)
    
    @classmethod
    def is_sound(cls,name):
        """
        Checks if ``name`` refers to a sound file
        
        The method searches the **Sounds** folder for the given file name.
        
        :param name: The file name
        :type name:  ``str``
        
        :return: True if ``name`` refers to a sound file; False otherwise
        :rtype:  ``bool``
        """
        if type(name) != str:
            return False
        
        return os.path.exists(os.path.join(cls.sounds,name))
    
    @classmethod
    def is_json(cls,name):
        """
        Checks if ``name`` refers to a JSON file
        
        The method searches the **JSON** folder for the given file name.
        
        :param name: The file name
        :type name:  ``str``
        
        :return: True if ``name`` refers to a sound file; False otherwise
        :rtype:  ``bool``
        """
        if type(name) != str:
            return False
        elif name[-4:].lower() != 'json':
            return False
        
        return os.path.exists(os.path.join(cls.json,name))
    
    @classmethod
    def load_texture(cls,name):
        """
        Returns: The texture for the given file name, or None if it cannot be loaded
        
        The ``name`` must refer to the file in the **Images** folder.  If the texture
        has already been loaded, it will return the cached texture.  Otherwise, it will
        load the texture and cache it before returning it.
        
        :param name: The file name
        :type name:  ``str``
        """
        if not cls.is_image(name):
            Logger.info('GameApp: No image file named %s.' % repr(name))
            return None
        elif name in cls.TEXTURE_CACHE:
            return cls.TEXTURE_CACHE[name]
        
        try:
            from kivy.core.image import Image
            texture = Image(name).texture
            cls.TEXTURE_CACHE[name] = texture
        except:
            Logger.info('GameApp: Image %s is not properly formatted.' % repr(name))
            exc_type, exc_value, exc_tb = sys.exc_info()
            items = traceback.format_exception(exc_type, exc_value, exc_tb)
            Logger.info(items[-1].strip())
            texture = None
        
        return texture
    
    @classmethod
    def unload_texture(cls,name):
        """
        Returns: The texture for the given file name, or None if it does not exist
        
        The ``name`` should refer to the file in in the texture cache.  If the texture
        is in the cache, it will return the cached texture before removing it.  Otherwise, 
        it will return None.
        
        :param name: The file name
        :type name:  ``str``
        """
        assert type(name) == str, '%s is not a valid texture name' % repr(name)
        if name in cls.TEXTURE_CACHE:
            texture = cls.TEXTURE_CACHE[name]
            del cls.TEXTURE_CACHE[name]
            return texture
        
        return None
    
    @classmethod
    def load_json(cls,name):
        """
        Returns: The JSON for the given file name, or None if it cannot be loaded
        
        The ``name`` must refer to the file in the **JSON** folder.  If the file is
        not there, it will return None.
        
        :param name: The file name
        :type name:  ``str``
        """
        if not cls.is_json(name):
            Logger.info('GameApp: No json file named %s.' % repr(name))
            return None
        
        data = None
        with open(os.path.join(cls.json,name)) as f: 
            data = f.read()
        
        if not data is None:
            try:
                data = json.loads(data)
            except Exception as e:
                Logger.info('GameApp: JSON %s is not properly formatted.' % repr(name))
                exc_type, exc_value, exc_tb = sys.exc_info()
                items = traceback.format_exception(exc_type, exc_value, exc_tb)
                Logger.info(items[-1].strip())
                data = None
        return data
    
    # BUILT-IN METHODS
    def __init__(self,**keywords):
        """
        Creates, but does not start, a new game.
        
        To use the constructor for this class, you should provide it with a list of
        keyword arguments that initialize various attributes. The primary user defined 
        attributes are the window ``width`` and ``height``. For example, to create a game 
        that fits inside of a 400x400 window, the constructor::
            
            GameApp(width=400,height=400)
        
        The game window will not show until you start the game. To start the game, use 
        the method ``run()``.
        
        **You will never call the constructor or run yourself**.  That is handled for 
        you in the provided code.
        
        :param keywords: dictionary of keyword arguments 
        :type keywords:  keys are attribute names
        """
        w = keywords.pop('width', 0.0)
        h = keywords.pop('height', 0.0)
        f = keywords.pop('fps', 60.0)
        
        assert type(w) in [int,float], 'width %s is not a number' % repr(w)
        assert type(h) in [int,float], 'height %s is not a number' % repr(h)
        assert type(f) in [int,float], 'fps %s is not a number' % repr(value)
        assert f > 0, 'fps %s is not positive' % repr(value)
        
        self._gwidth = w
        self._gheight = h
        Window.size = (self.width,self.height)
        
        self._fps = f
        
        x = keywords.pop('left', None)
        y = keywords.pop('top', None)
        assert x is None or type(x) in [int,float], 'left edge %s is not a number' % repr(x)
        assert y is None or type(y) in [int,float], 'top edge %s is not a number' % repr(y)
        
        if not x is None:
            Window.left = x
        if not y is None:
            Window.top = y
        
        x = keywords.pop('right', None)
        y = keywords.pop('bottom', None)
        assert x is None or type(x) in [int,float], 'right edge %s is not a number' % repr(x)
        assert y is None or type(y) in [int,float], 'bottom edge %s is not a number' % repr(y)
        
        if not x is None:
            Window.left = x-self.width
        if not y is None:
            Window.top = y+self.height
        
        self._setpaths()
        
        # Tell Kivy to build the application
        kivy.app.App.__init__(self,**keywords)
    
    
    # PUBLIC METHODS
    def build(self):
        """
        Initializes the graphics window.
        
        This is a Kivy reserved method.  It is part of the Kivy application process.  
        It should **never** be overridden.
        """
        from .gview import GInput, GView
        self._view = GView()
        self._view.size_hint = (1,1)
        self._input = GInput()
        self._input._register(self._view)
        return self.view
    
    def run(self):
        """
        Displays the game window and starts the game.
        
        This is a Kivy reserved method.  It is part of the Kivy application process.  
        It should **never** be overridden.
        """
        Clock.schedule_once(self._bootstrap,-1)
        kivy.app.App.run(self)
    
    def stop(self):
        """
        Closes the game window and exit Python.
        
        This is a Kivy reserved method.  It is part of the Kivy application process.  
        It should **never** be overridden.
        """
        import sys
        kivy.app.App.stop(self)
        sys.exit(0)
    
    def start(self):
        """
        Initializes the game state, creating a new game.
        
        This method is distinct from the built-in initializer ``__init__``, which has been
        hidden from you. This method is called once the game is running.  You should use
        it to initialize any game specific attributes. 
        
        **Never override the built-in method __init__**
        """
        pass
    
    def update(self,dt):
        """
        Updates the state of the game one animation frame.
        
        This method is called 60x a second (depending on the ``fps``) to provide on-screen 
        animation. Any code that moves objects or processes user input (keyboard or mouse)
        goes in this method.
        
        Think of this method as the body of the loop.  You will need to add attributes
        that represent the current animation state, so that they can persist across
        animation frames.  These attributes should be initialized in `start`.
        
        :param dt: time in seconds since last update
        :type dt:  ``int`` or ``float``
        """
        pass
    
    def draw(self):
        """
        Draws the game objects on the screen.
        
        Every single object that you draw will need to be an attribute of the ``GameApp``
        class.  This method should largely be a sequence of calls to ``self.view.draw()``.
        """
        pass
    
    
    # HIDDEN METHODS
    def _bootstrap(self,dt):
        """
        Bootstraps the clock scheduler for the game..
        
        This method is a callback-proxy for method `start`.  It handles important issues 
        behind the scenes, particularly with setting the FPS
        """
        if (self.fps < 60):
            Clock.schedule_interval(self._refresh,1.0/self.fps)
        else:
            Clock.schedule_interval(self._refresh,0)
        self.start()
    
    def _refresh(self,dt):
        """
        Processes a single animation frame.
        
        This method a callback-proxy for the methods `update` and `draw`.  It handles
        important issues behind the scenes, particularly with clearing the window.
        
        :param dt: time in seconds since last update
        :type dt:  ``int`` or ``float``
        """
        self.view.clear()
        self.update(dt)
        self.draw()
        self.input.refresh()
    
    def _setpaths(self):
        """
        Sets the resource paths to the application directory.
        """
        # This prevents us from running two game simultaneously
        # But kivy already prevents this from happening
        import os, sys
        import inspect
        
        path = os.path.abspath(inspect.getfile(self.__class__))
        path = os.path.dirname(path)
        
        GameApp.json   = str(os.path.join(path, 'JSON'))
        GameApp.fonts  = str(os.path.join(path, 'Fonts'))
        GameApp.sounds = str(os.path.join(path, 'Sounds'))
        GameApp.images = str(os.path.join(path, 'Images'))
        
        import kivy.resources
        kivy.resources.resource_add_path(GameApp.fonts)
        kivy.resources.resource_add_path(GameApp.sounds)
        kivy.resources.resource_add_path(GameApp.images)

