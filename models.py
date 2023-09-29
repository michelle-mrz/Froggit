"""
Models module for Froggit

This module contains the model classes for the Frogger game. Anything that you
interact with on the screen is model: the frog, the cars, the logs, and so on.

Just because something is a model does not mean there has to be a special class for
it. Unless you need something special for your extra gameplay features, cars and logs
could just be an instance of GImage that you move across the screen. You only need a new
class when you add extra features to an object.

That is why this module contains the Frog class.  There is A LOT going on with the
frog, particularly once you start creating the animation coroutines.

If you are just working on the main assignment, you should not need any other classes
in this module. However, you might find yourself adding extra classes to add new
features.  For example, turtles that can submerge underneath the frog would probably
need a custom model for the same reason that the frog does.

If you are unsure about  whether to make a new class or not, please ask on Piazza. We
will answer.

# Michelle Ren Zhang [mr897]
# 12.21.20
"""
from consts import *
from game2d import *

# PRIMARY RULE: Models are not allowed to access anything in any module other than
# consts.py.  If you need extra information from a lane or level object, then it
# should be a parameter in your method.


class Frog(GSprite):         # You will need to change this by Task 3
    """
    A class representing the frog

    The frog is represented as an image (or sprite if you are doing timed animation).
    However, unlike the obstacles, we cannot use a simple GImage class for the frog.
    The frog has to have additional attributes (which you will add).  That is why we
    make it a subclass of GImage.

    When you reach Task 3, you will discover that Frog needs to be a composite object,
    tracking both the frog animation and the death animation.  That will like caused
    major modifications to this class.
    """
    # LIST ALL HIDDEN ATTRIBUTES HERE
    # Attribute _death: Death animation that gets executed when frog dies
    # Invariant: _death is a GSprite object

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getX(self):
        """
        Returns: the x-coordinate of the frog's current position.
        """
        return self.x

    def setX(self,value):
        """
        Sets the x-coordinate of the frog position to value.

        Parameter value: the frog new position's x-coordinate
        Precondition: value is a valid number within the game window
        (floar or int)
        """
        self.x = value

    def getY(self):
        """
        Returns: the y-coordinate of the frog's current position.
        """
        return self.y

    def setY(self,value):
        """
        Sets the y-coordinate of the frog position to value.

        Parameter value: the frog new position's y-coordinate
        Precondition: value is a valid number within the game window
        (floar or int)
        """
        self.y = value

    def setAngle(self,value):
        """
        Sets the frog's angle.

        The frog heading's angles are defined in the file consts.py. FROG_NORTH
        is 180, FROG_WEST is -90, FROG_EAST is 90 and FROG_SOUTH is 0.

        Parameter value: the frog's new angle
        Precondition: value is an int or a float
        """
        self.angle = value

    def getDeath(self):
        """
        Returns death sprite.
        """
        return self._death

    # INITIALIZER TO SET FROG POSITION
    def __init__(self,x,y,object):
        """
        Initializes the frog that plays the game.

        Parameter x: the x-coordinate of the frog's center
        Precondition: value is a valid number within the window (floar or int)

        Parameter y: the y-coordinate of the frog's center
        Precondition: value is a valid number within the window (floar or int)

        Parameter object: JSON file that contains additional information about
        image files
        Precondition: object is a dictionary (not for a level file)
        """
        frog_source = FROG_SPRITE + '.png'
        super().__init__(source=frog_source,frame=0,
                        hitboxes=object['sprites']['frog']['hitboxes'],
                        format=object['sprites']['frog']['format'])
        self.x = (x+0.5)*GRID_SIZE
        self.y = (y+0.5)*GRID_SIZE
        self.angle = FROG_NORTH
        death_source = DEATH_SPRITE + '.png'
        self._death = GSprite(x=self.x,y=self.y,width=self.width,
                    height=self.height,source=death_source,frame=0,
                    format=object['sprites']['skulls']['format'])
        # self.frame = 0
        # self.hitboxes = object['sprites']['frog']['hitboxes']
        # self.frame = object['sprites']['frog']['frame']

    # ADDITIONAL METHODS (DRAWING, COLLISIONS, MOVEMENT, ETC)
    def animateVertical(self,direction):
        """
        Animates the frog's up and down movements over FROG_SPEED seconds.

        This method is a coroutine that takes a break (so that the game
        can redraw the image) every time it moves it. The coroutine takes
        the dt as periodic input so it knows how many (parts of) seconds
        to animate.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float or int.

        Parameter direction: The direction to rotate.
        Precondition: direction is a string and one of 'up' or 'down'.
        """
        svert = self.y
        if direction == 'up':
            fvert = svert+GRID_SIZE
        if direction == 'down':
            fvert = svert-GRID_SIZE

        steps = (fvert-svert)/FROG_SPEED
        time = 0
        animating = True
        while animating:
            dt = (yield)
            amount = steps*dt
            self.y = self.y+amount
            time = time+dt

            if abs(self.y-svert) >= GRID_SIZE:
                self.y = fvert
                animating = False

            frac = (self.y-svert)/(fvert-svert)
            if frac < 1:
                frame = 4+frac*(0-4)
                self.frame = round(frame)
            else:
                frac = frac-1
                frame = 0+frac*4
                self.frame = round(frame)

    def animateHori(self,direction):
        """
        Animates the frog's left and right movements over FROG_SPEED seconds

        This method is a coroutine that takes a break (so that the game
        can redraw the image) every time it moves it. The coroutine takes
        the dt as periodic input so it knows how many (parts of) seconds
        to animate.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is an int or float.

        Parameter direction: The direction to rotate.
        Precondition: direction is a string and one of 'left' or 'right'.
        """
        svert = self.x
        if direction == 'right':
            fvert = svert+GRID_SIZE
        if direction == 'left':
            fvert = svert-GRID_SIZE

        steps = (fvert-svert)/FROG_SPEED
        time = 0
        animating = True
        # animating = (time<FROG_SPEED)
        while animating:
            dt = (yield)
            amount = steps*dt
            self.x = self.x+amount
            time = time+dt

            if abs(self.x-svert) >= GRID_SIZE:
                self.x = fvert
                animating = False

            frac = (self.x-svert)/(fvert-svert)
            if frac < 1:
                frame = 4+frac*(0-4)
                self.frame = round(frame)
            else:
                frac = frac-1
                frame = 0+frac*(4)
                self.frame = round(frame)

    def animateDeath(self):
        """
        Animates death over DEATH_SPEED seconds.

        This method is a coroutine that takes a break (so that the game
        can redraw the image) every time it moves it. The coroutine takes
        the dt as periodic input so it knows how many (parts of) seconds
        to animate.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is an int or float.
        """
        animating = True
        time = 0
        while animating:
            dt = (yield)
            time = time + dt

            if time>DEATH_SPEED:
                animating = False

            frac = time/DEATH_SPEED
            if frac < 1:
                frame = 7+frac*(0-7)
                self.frame = round(frame)

# IF YOU NEED ADDITIONAL LANE CLASSES, THEY GO HERE
