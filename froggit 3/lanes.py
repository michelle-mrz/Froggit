"""
Lanes module for Froggit

This module contains the lane classes for the Frogger game. The lanes are the vertical
slice that the frog goes through: grass, roads, water, and the exit hedge.

Each lane is like its own level. It has hazards (e.g. cars) that the frog has to make
it past.  Therefore, it is a lot easier to program frogger by breaking each level into
a bunch of lane objects (and this is exactly how the level files are organized).

You should think of each lane as a secondary subcontroller.  The level is a subcontroller
to app, but then that subcontroller is broken up into several other subcontrollers, one
for each lane.  That means that lanes need to have a traditional subcontroller set-up.
They need their own initializer, update, and draw methods.

There are potentially a lot of classes here -- one for each type of lane.  But this is
another place where using subclasses is going to help us A LOT.  Most of your code will
go into the Lane class.  All of the other classes will inherit from this class, and
you will only need to add a few additional methods.

If you are working on extra credit, you might want to add additional lanes (a beach lane?
a snow lane?). Any of those classes should go in this file.  However, if you need additional
obstacles for an existing lane, those go in models.py instead.  If you are going to write
extra classes and are now sure where they would go, ask on Piazza and we will answer.

# Michelle Ren Zhang [mr897]
# 12.21.20
"""
from game2d import *
from consts import *
from models import *

# PRIMARY RULE: Lanes are not allowed to access anything in any level.py or app.py.
# They can only access models.py and const.py. If you need extra information from the
# level object (or the app), then it should be a parameter in your method.

class Lane(object):         # You are permitted to change the parent class if you wish
    """
    Parent class for an arbitrary lane.

    Lanes include grass, road, water, and the exit hedge.  We could write a class for
    each one of these four (and we will have classes for THREE of them).  But when you
    write the classes, you will discover a lot of repeated code.  That is the point of
    a subclass.  So this class will contain all of the code that lanes have in common,
    while the other classes will contain specialized code.

    Lanes should use the GTile class and to draw their background.  Each lane should be
    GRID_SIZE high and the length of the window wide.  You COULD make this class a
    subclass of GTile if you want.  This will make collisions easier.  However, it can
    make drawing really confusing because the Lane not only includes the tile but also
    all of the objects in the lane (cars, logs, etc.)
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _tile: background image of lanes
    # Invariant: _tile is a GTile object
    #
    # Attribute _objs: contains all obstacles in a lane
    # Invariant: _objs is a list of GImage objects
    #
    # Attribute _speed: speed in which the obstacles move
    # Invariant: _speed is a number (int or float)
    #
    # Attribute _buffer: distance in grids that the objects are allowed to go
    # offscreen
    # Invariant: _buffer is a number (int or float)

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getTile(self):
        """
        Returns inidividual tile backgrounds.
        """
        return self._tile

    def getSpeed(self):
        """
        Returns speed at which the obstacles are moving.
        """
        return self._speed

    # INITIALIZER TO SET LANE POSITION, BACKGROUND,AND OBJECTS
    def __init__(self,json,i,w,object): #idk if i need x and y
        """
        Initializes the composite Lane object that are drawn in the game.

        Lane is a composite object and is the parent class for the classes
        Grass, Road, Water, and Hedge. It initializes the background images
        of each individual lane (which are GTile objects) and the obstacles
        that move or are positioned in each lane (which are GImage objects).
        It also initializes additional attributes that will help the obstacles
        move once the game begins.

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
        self._objs = []

        # tile
        name = json['lanes'][i]['type']
        fullname = name + '.png'
        if i == 0:
            lanes = GTile(left=0,bottom=0,width=w*GRID_SIZE,height=GRID_SIZE,
                            source=fullname)
            self._tile = lanes
        else:
            lanes = GTile(left=0,bottom=GRID_SIZE+GRID_SIZE*(i-1),
                        width=w*GRID_SIZE,height=GRID_SIZE,source=fullname)
            self._tile = lanes

        if 'objects' in json['lanes'][i]:
            for j in range(len(json['lanes'][i]['objects'])):
                objname = json['lanes'][i]['objects'][j]['type']
                fullobjname = objname + '.png'
                pos = json['lanes'][i]['objects'][j]['position']
                hit = object['images'][objname]['hitbox']
                obstacle = GImage(x=(pos+0.5)*GRID_SIZE,y=self._tile.y,
                            source=fullobjname,hitbox=hit)
                if 'speed' in json['lanes'][i]:
                    speed = json['lanes'][i]["speed"]
                    if speed < 0:
                        obstacle = GImage(x=(pos+0.5)*GRID_SIZE,y=self._tile.y,
                        source=fullobjname,angle=180,hitbox=hit)
                self._objs.append(obstacle)

        # lane speed
        if 'speed' in json['lanes'][i]:
            self._speed = json['lanes'][i]['speed']

        # buffer
        self._buffer = json['offscreen']

    # ADDITIONAL METHODS (DRAWING, COLLISIONS, MOVEMENT, ETC)
    def update(self,dt,w):
        """
        Updates the movement of the obstacles in a line.

        This method updates the horizontal coordinate of the obstacles in order
        to make them move. The obstacles movements are determined by the 'speed'
        of the lane which is the number of pixels that each obstacle should
        move per second. All obstacles in a lane move at the same rate. When
        the obstacles go offscreen, this method also wraps them back around the
        other side.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is a int or float.

        Paramter w: the window's width
        Precondition: w is a number>0 (int or float)
        """
        width = w*GRID_SIZE
        speed = self._speed*dt
        buffer_right = width + (self._buffer*GRID_SIZE)
        buffer_left = 0 - (self._buffer*GRID_SIZE)
        # print(str(buffer_right) + 'right buffer')
        # print(str(buffer_left) + 'left buffer')

        for obs in self._objs:
            obs.x = obs.x + speed
            if speed>0: # moves left to right -->
                if obs.x >= buffer_right:
                    d = buffer_right-obs.x
                    obs.x = buffer_left + d
            elif speed<0: # moves right to left <--
                if obs.x <= buffer_left:
                    d = obs.x-buffer_left
                    obs.x = buffer_right - d

    def draw(self,view):
        """
        Draws the obstacles.

        Parameter view: the view (is a reference to the window)
        Precondition: view is a GView object
        """
        self._tile.draw(view)
        for obs in self._objs:
            obs.draw(view)

    def collision(self,frog):
        """
        Returns: True if the object has collided with a tile.

        This method uses collides() to checks if the tile and the frog are
        overlapping.

        Parameter frog: the frog that is playing the game
        Precondition: frog is Frog object
        """
        return self._tile.collides(frog)


class Grass(Lane):                           # We recommend AGAINST changing this one
    """
    A class representing a 'safe' grass area.

    You will NOT need to actually do anything in this class.  You will only do anything
    with this class if you are adding additional features like a snake in the grass
    (which the original Frogger does on higher difficulties).
    """
    pass

    # ONLY ADD CODE IF YOU ARE WORKING ON EXTRA CREDIT EXTENSIONS.


class Road(Lane):                           # We recommend AGAINST changing this one
    """
    A class representing a roadway with cars.

    If you implement Lane correctly, you do really need many methods here (not even an
    initializer) as this class will inherit everything.  However, roads are different
    than other lanes as they have cars that can kill the frog. Therefore, this class
    does need a method to tell whether or not the frog is safe.
    """

    # DEFINE ANY NEW METHODS HERE
    def squash(self,frog):
        """
        Returns True if the frog has collided with a car.

        This method loops through the obstacle list in the Road lane to check if
        the frog has collided with a car. If it does, it return True.

        Parameter frog: the frog that is playing the game
        Precondition: frog is a Frog object
        """
        num = 0

        for obs in self._objs:
            if obs.collides(frog) == True:
                num = num + 1
                return num>=1 # returns None?


class Water(Lane):
    """
    A class representing a waterway with logs.

    If you implement Lane correctly, you do really need many methods here (not even an
    initializer) as this class will inherit everything.  However, water is very different
    because it is quite hazardous. The frog will die in water unless the (x,y) position
    of the frog (its center) is contained inside of a log. Therefore, this class needs a
    method to tell whether or not the frog is safe.

    In addition, the logs move the frog. If the frog is currently in this lane, then the
    frog moves at the same rate as all of the logs.
    """

    # DEFINE ANY NEW METHODS HERE
    def safe(self,frog):
        """
        Returns: True if the frog is safe (on a log)

        This method loops through the water obstacles (logs) to check if they
        contain the frog. If a log contains the frog, the frog is safe and
        the method returns True.

        Parameter frog: the frog that is playing the game
        Precondition: frog is a Frog object
        """
        num = 0
        point = (frog.getX(),frog.getY())

        for obs in self._objs:
            if obs.contains(point):
                num = num+1
                return num>=1


class Hedge(Lane):
    """
    A class representing the exit hedge.

    This class is a subclass of lane because it does want to use a lot of the features
    of that class. But there is a lot more going on with this class, and so it needs
    several more methods.  First of all, hedges are the win condition. They contain exit
    objects (which the frog is trying to reach). When a frog reaches the exit, it needs
    to be replaced by the blue frog image and that exit is now "taken", never to be used
    again.

    That means this class needs methods to determine whether or not an exit is taken.
    It also need to take the (x,y) position of the frog and use that to determine which
    exit (if any) the frog has reached. Finally, it needs a method to determine if there
    are any available exits at all; once they are taken the game is over.

    These exit methods will require several additional attributes. That means this class
    (unlike Road and Water) will need an initializer. Remember to user super() to combine
    it with the initializer for the Lane.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _exitlist: list that stores occupied exits
    # Invariant: _exitlist is a list of GImage objects
    #
    # Attribute _blues: list of safe blue frogs that appears on a taken exit
    # Invariant: _blues is a GImage object

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    # INITIALIZER TO SET ADDITIONAL EXIT INFORMATION
    def __init__(self,json,i,w,object):
        """
        Initializes list that stores safe blue frogs and list that keeps track
        of occupied exits.

        When a frog touches the exit, the exit becomes blocked and thus a
        safe blue frog should be put on top of the taken exit. In order to block
        exits, it is necessary to keep track of which exits are taken.

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
        super().__init__(json,i,w,object)

        self._exitlist = []
        self._blues = []

    # ANY ADDITIONAL METHODS
    def update(self,frog):
        """
        Updates whether exits are taken and whether safe blue frogs should be
        created.

        This method updates occupied exits. If the exit is occupied, it
        get appended to a list with all other occupied exits and creates the
        safe blue frog that goes on top of it.

        Parameter frog: the frog that is playing the game
        Precondition: frog is a Frog object
        """
        point = (frog.getX(),frog.getY())

        for obs in self._objs:
            if obs.source != 'open.png':
                if obs.contains(point) == True and obs not in self._exitlist:
            # if self._taken == True:
                    blue = GImage(x=obs.x,y=obs.y,source=FROG_SAFE)
                    self._exitlist.append(obs)
                    self._blues.append(blue)

    def draw(self,view):
        """
        Draws the safe blue frogs.

        Parameter view: the view (is a reference to the window)
        Precondition: view is a GView object
        """
        super().draw(view)

        for blue in self._blues:
            blue.draw(view)

    def containment(self,frog):
        """
        Returns: True if frog is contained in a Hedge obstacle.

        This method loops through the obstacles in Hedge and checks if the
        frog's center is contained in the obstacle. It returns True if it is.

        Parameter frog: the frog that is playing the game
        Precondition: frog is a Frog object
        """
        # self._taken = False
        point = (frog.getX(),frog.getY()) # tuple

        num = 0

        for obs in self._objs:
            # if obs.source != 'open.png':
            if obs.contains(point) == True:
                num = num + 1
                return num>=1 # returns None? # this is always returning True

    def block(self,frog):
        """
        Returns True if the exit is blocked.

        This method checks if an exit is taken (the frog moved into it and the
        safe blue frog was drawn).

        Parameter frog: the frog that is playing the game
        Precondition: frog is Frog object
        """
        point = (frog.getX(),frog.getY())

        for obs in self._objs:
            if obs.source != 'open.png':
                if obs.contains(point) == True:
                    return obs in self._exitlist

    def all_used(self):
        """
        Returns True if all exits are occupied.

        This method checks that all exits on the hegde tile are taken
        (frog moved into all of them and safe blue frogs were drawn in all
        of them). If they are all occupied, the method return True, False
        othewise
        """
        num_obs = 0

        for obs in self._objs:
            if obs.source != 'open.png':
                num_obs = num_obs + 1

        return len(self._exitlist) == num_obs

    def opening(self,frog):
        """
        Returns True if the frog is contained in an opening.

        This method checks whether the frog is on an opening. The frog can move
        freely through openings unlike exits where it can only be reached into
        once from the north before being blocked.

        Parameter frog: the frog that is playing the game
        Precondition: frog is a Frog object
        """
        point = (frog.getX(),frog.getY())
        num = 0

        for obs in self._objs:
            # if obs.source != 'open.png':
            if obs.contains(point) == True:
                if obs.source == 'open.png':
                    num = num + 1
                    return num>=1

# IF YOU NEED ADDITIONAL LANE CLASSES, THEY GO HERE
