"""
Primary module for Froggit

This module contains the main controller class for the Froggit application. There
is no need for any additional classes in this module.  If you need more classes, 99%
of the time they belong in either the lanes module or the models module. If you are
unsure about where a new class should go, post a question on Piazza.

# Michelle Ren Zhang [mr897]
# 12.21.20
"""
from consts import *
from game2d import *
from level import *
import introcs

from kivy.logger import Logger


# PRIMARY RULE: Froggit can only access attributes in level.py via getters/setters
# Froggit is NOT allowed to access anything in lanes.py or models.py.


class Froggit(GameApp):
    """
    The primary controller class for the Froggit application

    This class extends GameApp and implements the various methods necessary for
    processing the player inputs and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Level object

        Method draw displays the Level object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Level.
    Level should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is managing the game state: when is the
    game started, paused, completed, etc. It keeps track of that in a hidden
    attribute

    Attribute view: The game view, used in drawing (see examples from class)
    Invariant: view is an instance of GView and is inherited from GameApp

    Attribute input: The user input, used to control the frog and change state
    Invariant: input is an instance of GInput and is inherited from GameApp
    """
    # HIDDEN ATTRIBUTES
    # Attribute _state: The current state of the game (taken from consts.py)
    # Invariant: _state is one of STATE_INACTIVE, STATE_LOADING, STATE_PAUSED,
    #            STATE_ACTIVE, STATE_CONTINUE, or STATE_COMPLETE
    #
    # Attribute _level: The subcontroller for a level, managing the frog and obstacles
    # Invariant: _level is a Level object or None if no level is currently active
    #
    # Attribute _title: The title of the game
    # Invariant: _title is a GLabel, or None if there is no title to display
    #
    # Attribute _text: A message to display to the player
    # Invariant: _text is a GLabel, or None if there is no message to display

    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # Attribute _lastkeys: The number of keys pressed last frame
    # Invariant: _lastkeys: is an int >= 0

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.
        """
        self._state = STATE_INACTIVE
        self._level = None
        self._lastkeys = 0
        self._title = GLabel(text='FROGGIT',linecolor='dark green',
                            font_name=ALLOY_FONT,font_size=ALLOY_LARGE,
                            x=self.width/2,y=self.height/2)
        self._text = GLabel(text="Press 'S' to start",font_name=ALLOY_FONT,
                            font_size=ALLOY_MEDIUM,x=self.width/2,
                            top=self._title.bottom)

    def update(self,dt):
        """
        Updates the game objects each frame.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # Determine current state
        self._determineState()

        # Process states
        if self._state == STATE_INACTIVE:
            self._text.top = self._title.bottom
        if not self._state == STATE_INACTIVE:
            self._title = None
        if self._state == STATE_ACTIVE:
            self._text = None

        # draw objects
        if self._state == STATE_LOADING:
            d = self.load_json(DEFAULT_LEVEL)
            object = self.load_json(OBJECT_DATA)
            self._resizeWindow(d)
            self._level = Level(d,object)
            # print(self._state)
            # print(self._level)
            self._state = STATE_ACTIVE

        if self._state == STATE_ACTIVE:
            self._switchActive(dt)

        if self._state == STATE_PAUSED:
            # print(self._state)
            h = self.height-GRID_SIZE
            self._text = GLabel(text="Press 'C' to Continue",
                        fillcolor='dark green',linecolor='white',
                        font_name=ALLOY_FONT,font_size=ALLOY_SMALL,
                        x=self.width/2,y=h/2,width=self.width,height=GRID_SIZE)

        if self._state == STATE_CONTINUE:
            # frog initial position
            d = self.load_json(DEFAULT_LEVEL)
            object = self.load_json(OBJECT_DATA)
            x = d['start'][0]
            y = d['start'][1]
            # reset frog to initial position
            self._level.setFrog(x,y,object)
            self._state = STATE_ACTIVE

    def draw(self):
        """
        Draws the game objects to the view.
        """
        if self._state == STATE_INACTIVE:
            self._title.draw(self.view)
            self._text.draw(self.view)

        if not self._level == None:
            self._level.draw(self.view)

        if self._state == STATE_PAUSED:
            # print('draw')
            self._text.draw(self.view)

        if self._state == STATE_COMPLETE:
            self._text.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE
    def _determineState(self):
        """
        Determines the current state of the game and assigns it to self._state.
        """
        # Determine current number of keys pressed
        curr_keys = self.input.key_count

        # Determine if S is being pressed
        is_s = self.input.is_key_down('s')

        # Only if we have pressed key for this one animation frame
        change = (curr_keys > 0) and (self._lastkeys == 0)

        if change and is_s and self._state == STATE_INACTIVE:
            self._state = STATE_LOADING

        # Deterine if C is being pressed
        is_c = self.input.is_key_down('c')

        if change and is_c and self._state == STATE_PAUSED:
            self._state = STATE_CONTINUE

        # Update last keys
        self._lastkeys = curr_keys
        # print(self._lastkeys)

    def _switchActive(self,dt):
        """
        Switches state from STATE_ACTIVE to STATE_COMPLETE or STATE_PAUSED.
        
        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._level.update(self.input,dt)
        if self._level.detectLives():
            self._state = STATE_COMPLETE
            h = self.height-GRID_SIZE
            self._text = GLabel(text="YOU DIED",
                        fillcolor='dark green',linecolor='white',
                        font_name=ALLOY_FONT,font_size=ALLOY_SMALL,
                        x=self.width/2,y=h/2,width=self.width,
                        height=GRID_SIZE)
        elif self._level.getFrog() == None:
            if self._level.getExit():
                self._state = STATE_COMPLETE
                h = self.height-GRID_SIZE
                self._text = GLabel(text="YOU WIN",fillcolor='dark green',
                            linecolor='white',font_name=ALLOY_FONT,
                            font_size=ALLOY_SMALL,x=self.width/2,y=h/2,
                            width=self.width,height=GRID_SIZE)
            else:
                self._state = STATE_PAUSED

    def _resizeWindow(self,d):
        """
        Resizes the window for each level.

        This method takes in the converted JSON nested dictionary and reasigns
        the attributes width and height to match the width and height
        values of its respective level.

        Parameter d: valid level JSON file
        Precondition: d is a dictionary for a valid level JSON
        """
        w = d["size"][0]
        h = d["size"][1]
        self.width = w*GRID_SIZE
        self.height = (h+1)*GRID_SIZE
