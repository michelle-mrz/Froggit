"""
Subcontroller module for Froggit

This module contains the subcontroller to manage a single level in the Froggit game.
Instances of Level represent a single game, read from a JSON.  Whenever you load a new
level, you are expected to make a new instance of this class.

The subcontroller Level manages the frog and all of the obstacles. However, those are
all defined in models.py.  The only thing in this class is the level class and all of
the individual lanes.

This module should not contain any more classes than Levels. If you need a new class,
it should either go in the lanes.py module or the models.py module.

# Michelle Ren Zhang [mr897]
# 12.21.20
"""
from game2d import *
from consts import *
from lanes  import *
from models import *

# PRIMARY RULE: Level can only access attributes in models.py or lanes.py using getters
# and setters. Level is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Level(object):
    """
    This class controls a single level of Froggit.

    This subcontroller has a reference to the frog and the individual lanes.  However,
    it does not directly store any information about the contents of a lane (e.g. the
    cars, logs, or other items in each lane). That information is stored inside of the
    individual lane objects.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lesson 27 for an example.  This class will be similar to that
    one in many ways.

    All attributes of this class are to be hidden.  No attribute should be accessed
    without going through a getter/setter first.  However, just because you have an
    attribute does not mean that you have to have a getter for it.  For example, the
    Froggit app probably never needs to access the attribute for the Frog object, so
    there is no need for a getter.

    The one thing you DO need a getter for is the width and height.  The width and height
    of a level is different than the default width and height and the window needs to
    resize to match.  That resizing is done in the Froggit app, and so it needs to access
    these values in the level.  The height value should include one extra grid square
    to suppose the number of lives meter.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _width: Width of the window in grid squares
    # Invariant: _width is an int or float > 0 extracted from the 'size' key of
    # a dictionary for a valid JSON level
    #
    # Attribute _height: Height of the window in grid squares
    # Invariant: _height is an int or float >0 extracted from the 'size' key of
    # a dictionary for a valid JSON level
    #
    # Attribute _lanes: list of tiles and obstacles to draw and animate
    # Invariant: _lanes is a list of Lane objects
    #
    # Attribute _frog: frog to play the game
    # Invariant: _frog is a Frog object (or None)
    #
    # Attribute _froghead: Images that represent the number of lives left
    # Invariant: _froghead is a list of GImage objects
    #
    # Attribute _liveslabel: Text that indicates lives
    # Invariant: _liveslabel is a GLabel object
    #
    # Attribute _exit: Checks if all exits are occupied
    # Invariant: _exit is a boolean that is True if all exits are occupied,
    # False otherwise
    #
    # Attribute _animator: A coroutine for performing an animation
    # Invariant: _animator is a generator-based coroutine (or None)
    #
    # Attribute _croak: The sound that frog makes when it moves
    # Invariant: _croak is a Sound object
    #
    # Attribute _splat: The sound that frog makes when it dies
    # Invariant: _splat is a Sound object
    #
    # Attribute _trill The sound that frog makes when it occupies an exit
    # Invariant: _trill is a Sound object

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getFrog(self):
        """
        Returns Frog object.
        """
        return self._frog

    def setFrog(self,x,y,object):
        """
        Sets the Frog object to another position.

        Parameter x: Valid grid position
        Precondition: x is a number (int or float)

        Parameter y: Valid grid position
        Precondition: y is a number (int or float)

        Parmeter object: JSON file
        Precondition: object is dictionary
        """
        self._frog = Frog(x,y,object)

    def getExit(self):
        """
        Returns: True if all exits are occupied, False otherwise
        """
        return self._exit

    # INITIALIZER (standard form) TO CREATE THE FROG AND LANES
    def __init__(self,json,object):
        """
        Initiliazes the frog, lanes, and lives counter.

        The frog is the one that moves and wins/loses the game, the lanes are
        the background tile images and their respective obstacles that can
        move, kill the frog or win the game, and the lives counter displays
        the number of lives the frog still has left before it is killed.

        Parameter json: level that is currently being played
        Precondition: json is a dictionary for a valid level JSON

        Parameter i: loop variable
        Precondition: i is an int>=0

        Paramter w: the window's width
        Precondition: w is a number>0 (int or float)

        Parameter object: JSON file that contains additional information about
        image files
        Precondition: object is a dictionary (not for a level file)
        """
        self._width = json['size'][0]
        self._height = json['size'][1]
        self._lanes = []
        self._exit = False
        # initial frog position from json string
        x = json['start'][0]
        y = json['start'][1]
        self._frog = Frog(x,y,object)
        # self._cooldown = FROG_SPEED
        self._animator = None
        self._croak = Sound(CROAK_SOUND)
        self._splat = Sound(SPLAT_SOUND)
        self._trill = Sound(TRILL_SOUND)
        self._killed = False

        self._initTiles(json,object)

        self._frogheads = []
        for i in range(FROG_LIVES):
            head = self._frogHead(i,FROG_LIVES,json)
            self._frogheads.append(head)

        self._liveslabel = GLabel(text='LIVES:',linecolor='dark green',
                            font_name=ALLOY_FONT,font_size=ALLOY_SMALL,
                            right=self._frogheads[0].left,
                            y=GRID_SIZE*(self._height+0.5))

    # UPDATE METHOD TO MOVE THE FROG AND UPDATE ALL OF THE LANES
    def update(self,input,dt):
        """
        Updates the frog, the inidividual lanes, and the lives counter
        as the game progresses.

        It is the method that is in charge of playing the game. It updates the
        frog position according to what keys the player presses (frog moves
        upwards if up arrow key is pressed, frog moves downwards if down arrow
        key is pressed, frog moves to the left if left arrow key is pressed,
        frog moves to the right if right arrow key is pressed). It also updates
        whether the frog has been killed (sets the frog to None) and removes
        lives from the lives counter as the game progresses.
        This method also updates the lanes and its respective obstacles by
        calling the update method in Lanes.

        Parameter input: Allows the game to register which key the player
        has pressed by accessing keyboard information
        Precondition: input is a GInput object

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()

        self._frogWater(dt)

        if not self._animator is None:
            try:
                self._animator.send(dt)
            except StopIteration:
                self._animator = None
        elif input.is_key_down('up'):
            self._moveUp()
        elif input.is_key_down('down'):
            self._moveDown()
        elif input.is_key_down('left'):
            self._moveLeft()
        elif input.is_key_down('right'):
            self._moveRight()

        self._blueFrog()

        self._frogWin()

        for lane in self._lanes:
            # grass and lanes dont have obstacles that move
            if isinstance(lane,Grass)==False and isinstance(lane,Hedge)==False:
                lane.update(dt,self._width)

        self._frogRoad()

        if self._checkWater() == False and self._animator == None:
            self._frogheads.pop()
            self._frog = None
            self._splat.play()

    # DRAW METHOD TO DRAW THE FROG AND THE INDIVIDUAL LANES
    def draw(self,view):
        """
        Draws the frog, the individual lanes, and the lives counter.

        Parameter view: the view (is a reference to the window)
        Precondition: view is a GView object
        """
        # draws lanes
        for lane in self._lanes:
            lane.draw(view)
            # take out of frog if crashes

        # draws frog
        if self._frog != None:
            self._frog.draw(view)

        # draws frog lives
        for head in self._frogheads:
            head.draw(view)

        # draws lives label
        self._liveslabel.draw(view)

    def detectLives(self):
        """
        Returns: True if the frog has no lives left

        This method checks that the frog has died FROG_LIVES times and has no
        lives left. It checks whether the length of the frog heads list is 0
        (every time the frog dies, one head of the life counter disappears).
        """
        return len(self._frogheads) == 0

    # ANY NECESSARY HELPERS (SHOULD BE HIDDEN)
    def _initTiles(self,json,object):
        """
        Helper that initializes Lane objects.

        This method is a helper function that helps the initializer initialize
        the inidividual lanes of a level.

        Parameter json: level that is currently being played
        Precondition: json is a dictionary for a valid level JSON

        Parameter object: JSON file that contains additional information about
        image files
        Precondition: object is a dictionary (not for a level file)
        """
        for i in range(len(json['lanes'])):
            name = json['lanes'][i]['type']
            if name == 'grass':
                lanes = Grass(json,i,self._width,object)
            elif name == 'road':
                lanes = Road(json,i,self._width,object)
            elif name == 'water':
                lanes = Water(json,i,self._width,object)
            elif name == 'hedge':
                lanes = Hedge(json,i,self._width,object)
            self._lanes.append(lanes)

    def _frogWater(self,dt):
        """
        Sets frog movement when frog is on top of a log.

        This method updates the frog position once it's on top of a log so that
        the log pushes the frog as the log moves. It also
        kills the frog if the frog's center goes off screen. This method checks
        whether the frog is on a log, checks if the tile that contains the frog
        is a Water object, then computes the new frog position based on the
        speed at which the logs move.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()
        point = (currentX,currentY)

        if self._checkWater():
            for lane in self._lanes:
                if isinstance(lane,Water):
                    if self._frog != None:
                        if lane.getTile().contains(point):
                            if self._animator == None:
                                speed = lane.getSpeed()*dt
                                self._frog.setX(currentX+speed)
                                spos = currentX+speed
                                if spos<=0 or spos>=self._width*GRID_SIZE:
                                    self._frogheads.pop()
                                    self._frog = None
                                    self._splat.play()

    def _frogRoad(self):
        """
        Kills the frog if it has collided with a car.

        This method checks if the frog has a collided with a car, and sets it to
        None (kills it) if the collision happens to be True. It also plays the
        splat sound the frog makes when it dies.
        """
        if self._checkRoad():
            self._frogheads.pop()
            # self._killed = True
            # self._animator = self._frog.animateDeath()
            # next(self._animator)
            self._frog = None
            self._splat.play()
            # self._killed = False

    def _blueFrog(self):
        """
        Occupies exit and places safe blue frog on lilypad.

        This method checks whether the frog is contained in an exit and whether
        the exit has been taken. If the frog is contained in an exit that has
        not yet been occupied, the method calls update() in Lanes to draw the
        safe blue frog on top of the exit and sets the Frog to None so that the
        game can restart (if there are more empty exits) or reach completion (if
        all exits have been filled).
        """
        if  self._checkHedge() and self._checkTaken() == False: # if its True
            for lane in self._lanes:
                if isinstance(lane,Hedge):
                    lane.update(self._frog)
                    self._trill.play()
            self._frog = None

    def _frogWin(self):
        """
        Checks if all exits are occupied.
        """
        win = []
        for lane in self._lanes:
            if type(lane) == Hedge:
                used = lane.all_used()
                win.append(used)
        if False not in win:
            self._exit = True

    def _moveUp(self):
        """
        Moves the frog upwards.

        This method moves the frog upwards when the up arrow key is being
        pressed. However, the frog cannot move outside the window or into
        hedge tiles and occupied exits.
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()

        self._frog.setAngle(FROG_NORTH)
        if currentY + GRID_SIZE <= self._height*GRID_SIZE:
            self._frog.setY(currentY+GRID_SIZE) # move frog upwards
            if self._checkHedge() == False or self._checkTaken() == True:
                self._frog.setY(currentY)
            elif  self._checkHedge() and self._checkTaken() == False:
                self._frog.setY(currentY)
                self._trill.play()
                self._animator = self._frog.animateVertical('up')
                next(self._animator)
            else:
                self._frog.setY(currentY)
                self._croak.play()
                self._animator = self._frog.animateVertical('up')
                next(self._animator)

    def _moveDown(self):
        """
        Moves the frog downwards.

        This method moves the frog downwards when the down arrow key is being
        pressed. However, the frog cannot move outside the window or move
        through unoccupied exits from the south. It can only move through Hegde
        objects if it's an opening.
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()

        self._frog.setAngle(FROG_SOUTH)
        if currentY - GRID_SIZE >= 0:
            self._frog.setY(currentY-GRID_SIZE)
            if self._checkOpening() == False:
                self._frog.setY(currentY)
            else:
                self._frog.setY(currentY)
                self._croak.play()
                self._animator = self._frog.animateVertical('down')
                next(self._animator)

    def _moveLeft(self):
        """
        Moves frog to the left.

        This method moves the frog to the left when the left arrow key is being
        pressed. However, the frog cannot move outside the window or move
        through Hedge objects unless it's an opening.
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()

        self._frog.setAngle(FROG_WEST)
        if currentX - GRID_SIZE >= 0:
            self._frog.setX(currentX-GRID_SIZE)
            if self._checkOpening() == False:
                self._frog.setX(currentX)
            else:
                self._frog.setX(currentX)
                self._croak.play()
                self._animator = self._frog.animateHori('left')
                next(self._animator)

    def _moveRight(self):
        """
        Moves frog to the right.

        This method moves the frog to the right when the right arrow key is
        being pressed. However, the frog cannot move outside the window or move
        through Hedge objects unless it's an opening.
        """
        currentX = self._frog.getX()
        currentY = self._frog.getY()

        self._frog.setAngle(FROG_EAST)
        if currentX + GRID_SIZE <= self._width*GRID_SIZE:
            self._frog.setX(currentX+GRID_SIZE)
            if self._checkOpening() == False:
                self._frog.setX(currentX)
            else:
                self._frog.setX(currentX)
                self._croak.play()
                self._animator = self._frog.animateHori('right')
                next(self._animator)

    def _frogHead(self,i,lives,json):
        """
        Returns: The inidivual frog head in the lives counter.

        This method creates the individual GImage objects (frog heads) that are
        drawn in the lives counter.

        Parameter i: loop variable
        Precondition: i is an int>=0

        Parameter lives: total amount of lives the player has
        Precondition: i is an int>0

        Parameter json: level that is currently being played
        Precondition: json is a dictionary for a valid level JSON
        """
        head = GImage(left=(self._width*GRID_SIZE)-((GRID_SIZE)*(FROG_LIVES-i)),
                    y=GRID_SIZE*(self._height+0.5),width=GRID_SIZE,
                    height=GRID_SIZE,source=FROG_HEAD)
        return head

    def _checkHedge(self):
        """
        Returns: True if the frog is contained within an exit, False if it
        collides with a hedge tile but is not contained in an exit.

        This method checks whether the frog in contained in an exit. If the
        Frog object is not None, it loops through the individual lanes,
        checks if the lane contains the frog's current position, checks if the
        lane's type is Hedge, checks whether the frog has collided with a
        hedge tile, and if all the conditions previously mentioned are
        met, it returns True if the frog is contained in an exit. If the frog
        has collided with a hedge tile but is not contained in an exit, it will
        return False.
        """
        # print('helper pos: ' + str(self._frog.getY()))
        # currentY = self._frog.getY()
        if self._frog != None:
            point = (self._frog.getX(),self._frog.getY())
            for lane in self._lanes: # loop thru lanes
                if lane.getTile().contains(point):
                    if isinstance(lane,Hedge): # check if its hedge
                        collides = lane.collision(self._frog)
                        if collides == True: # if its on hedge
                            contain = lane.containment(self._frog)
                            return contain == True

    def _checkRoad(self):
        """
        Returns: True if the frog has collided with a car, False otherwise.

        This method checks whether the frog has collided with a car. If the
        Frog object is not None, it loops through the individual lanes,
        checks if the lane contains the frog's current position, checks if the
        lane's type is Road, and if all the conditions previously mentioned are
        met, it returns True if the frog collides with a car obstacle.
        """
        if self._frog != None:
            for lane in self._lanes:
                point = (self._frog.getX(),self._frog.getY()) # tuple
                if lane.getTile().contains(point):
                    if isinstance(lane,Road):
                        squash = lane.squash(self._frog)
                        return squash == True

    def _checkWater(self):
        """
        Returns: True if the frog is on a log, False if it's on water

        This method checks whether the frog is on a log. If the
        Frog object is not None, it loops through the individual lanes,
        checks if the lane contains the frog's current position, checks if the
        lane's type is Water, and if all the conditions previously mentioned are
        met, it returns True if the frog is on a log. If the frog is on water
        but not a log, it returns False.
        """
        if self._frog != None:
            for lane in self._lanes:
                point = (self._frog.getX(),self._frog.getY()) # tuple
                if lane.getTile().contains(point):
                    if isinstance(lane,Water):
                        safe = lane.safe(self._frog)
                        return safe == True

    def _checkOpening(self):
        """
        Returns True if an opening contains the Frog, False otherwise.

        This method checks whether the an opening contains the Frog. Openings
        are Hedge obstacles with source 'open'. If the Frog object is not None,
        it loops through the individual lanes, checks if the lane contains the
        frog's current position, checks if the lane's type is Hedge, and if all
        the conditions previously mentioned are met, it returns True if the frog
        is contained in an opening.
        """
        if self._frog != None:
            for lane in self._lanes:
                point = (self._frog.getX(),self._frog.getY()) # tuple
                if lane.getTile().contains(point):
                    if isinstance(lane,Hedge):
                        opening = lane.opening(self._frog)
                        return opening == True

    def _checkTaken(self):
        """
        Returns: True if the exit is taken.

        This method checks whether exits in Hedge are occupied by safe frog. If
        an exit is occupied, it becomes blocked and the frog cannot longer move
        into it. If the Frog object is not None,
        it loops through the individual lanes, checks if the lane contains the
        frog's current position, checks if the lane's type is Hedge, and if all
        the conditions previously mentioned are met, it returns True if exit
        is blocked.
        """
        if not self._frog == None:
            for lane in self._lanes:
                point = (self._frog.getX(),self._frog.getY()) # tuple
                if lane.getTile().contains(point):
                    if isinstance(lane,Hedge):
                        return lane.block(self._frog)
