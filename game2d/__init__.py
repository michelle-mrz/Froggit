"""
A module to support simple 2D game development.

This module is a simple wrapper around Kivy interfaces to make 2D game development
simpler for students in CS 1110.

Author: Walker M. White (wmw2)
Date:   August 1, 2017 (Python 3 version)
"""
from .gobject import GObject, GScene
from .grectangle import GRectangle, GEllipse, GImage, GLabel
from .gsprite import GSprite
from .gtile import GTile
from .gpath import GPath, GTriangle, GPolygon
from .gview import GInput, GView
from .sound import Sound, SoundLibrary
from .app import GameApp