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

        This method is distinct from the built-in initializer __init__ (which
        you should not override or change). This method is called once the
        game is running. You should use it to initialize any game specific
        attributes.

        This method should make sure that all of the attributes satisfy the
        given invariants. When done, it sets the _state to STATE_INACTIVE and
        creates both the title (in attribute _title) and a message (in attribute
        _text) saying that the user should press a key to play a game.
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

        It is the method that does most of the work. It is NOT in charge of
        playing the game.  That is the purpose of the class Level. The primary
        purpose of this game is to determine the current state, and -- if the
        game is active -- pass the input to the Level object _level to play the
        game.

        As part of the assignment, you are allowed to add your own states.
        However, at a minimum you must support the following states:
        STATE_INACTIVE, STATE_LOADING, STATE_ACTIVE, STATE_PAUSED,
        STATE_CONTINUE, and STATE_COMPLETE.  Each one of these does its own
        thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.
        It is a paused state, waiting for the player to start the game.  It
        displays the title and a simple message on the screen. The application
        remains in this state so long as the player never presses a key.

        STATE_LOADING: This is the state that creates a new level and shows it on
        the screen. The application switches to this state if the state was
        STATE_INACTIVE in the previous frame, and the player pressed a key.
        This state only lasts one animation frame (the amount of time to load
        the data from the file) before switching to STATE_ACTIVE. One of the
        key things about this state is that it resizes the window to match the
        level file.

        STATE_ACTIVE: This is a session of normal gameplay. The player can
        move the frog towards the exit, and the game will move all obstacles
        (cars and logs) about the screen. All of this should be handled inside
        of class Level (NOT in this class).  Hence the Level class should have
        an update() method, just like the subcontroller example in lecture.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However,
        the game is still visible on the screen.

        STATE_CONTINUE: This state restores the frog after it was either killed
        or reached safety. The application switches to this state if the state
        was STATE_PAUSED in the previous frame, and the player pressed a key.
        This state only lasts one animation frame before switching to STATE_ACTIVE.

        STATE_COMPLETE: The wave is over (all lives are lost or all frogs are safe),
        and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

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

        Every single thing you want to draw in this game is a GObject. To draw a
        GObject g, simply use the method g.draw(self.view). It is that easy!

        Many of the GObjects (such as the cars, logs, and exits) are attributes
        in either Level or Lane. In order to draw them, you either need to add
        getters for these attributes or you need to add a draw method to
        those two classes.  We suggest the latter.  See the example subcontroller.py
        from the lesson videos.
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

        This method checks for a key press. A key press is when a key is pressed
        for the first time. We do not want the state to continue to change
        as we hold down the key. If the current state is STATE_INACTIVE and
        there is a key press that is 'S', it changes the state from
        SELF_INACTIVE to SELF_LOADING. If the current state is STATE_PAUSED and
        there is a key press that is 'C', it changes the state from
        STATE_PAUSED to STATE_CONTINUE. States are not changed for other key
        presses.
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

        If there are no lives left, the state is set to STATE_COMPLETE and
        the screen displays "YOU DIED". If all the exits have been occupied, it
        swtches the state to STATE_COMPLETE and the screen displays "YOU WIN".
        If there are still lives left or unoccupied exits, the state is switched
        to STATE_PAUSED.

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
