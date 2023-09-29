"""
Constants for Froggit

This module contains global constants for the game Froggit. These constants need to be
used in the model, the view, and the controller. As these are spread across multiple
modules, we separate the constants into their own module. This allows all modules to
access them.

# YOUR NAME AND NETID HERE
# DATE COMPLETED HERE
"""
import introcs
import sys

### WINDOW CONSTANTS (all coordinates are in pixels) ###

# The initial width of the game display
GAME_WIDTH  = 1024
# The initial height of the game display
GAME_HEIGHT = 896
# The size in pixels of a single grid square
GRID_SIZE    = 64


### FROG CONSTANTS ###

# The image file for the non-animated frog
FROG_IMAGE  = 'frog1.png'
# The number of seconds that frog movement takes
FROG_SPEED  = 0.25
# The image file for a frog that made it to safety
FROG_SAFE   = 'safe.png'
# The image file for a frog life
FROG_HEAD   = 'froghead.png'
# The number of lives the frog has before losing
FROG_LIVES  = 3

# The angles for the frog heading. Set the angle to these to get the right direction
# Notice the frog image is upside down, so NORTH requires a 180 degree rotation
FROG_NORTH  = 180
FROG_WEST   = -90
FROG_EAST   =  90
FROG_SOUTH  =   0

# The sprite sheet for the animated frog
FROG_SPRITE  = 'frog2'
# The sprite sheet for the dying frog
DEATH_SPRITE = 'skulls'
# The number of seconds for a death animation
DEATH_SPEED  = 0.5


### GAME CONSTANTS ###

# The state before the game has started
STATE_INACTIVE = 0
# The state when we are loading in a new level
STATE_LOADING  = 1
# The state when the level is activated and in play
STATE_ACTIVE   = 2
# The state when we are are paused between lives
STATE_PAUSED   = 3
# The state when we restoring the frog
STATE_CONTINUE = 4
# The state when the game is complete (won or lost)
STATE_COMPLETE = 5


### FONT CONSTANTS ###

# The font choice for labels and messages
ALLOY_FONT = 'AlloyInk.ttf'
# A large message or label
ALLOY_LARGE  = 124
# A medium message or label
ALLOY_MEDIUM = 64
# A small message or label
ALLOY_SMALL  = 48


### SOUND EFFECTS ###

# The jumping sound
CROAK_SOUND = 'croak.wav'
# The death sound
SPLAT_SOUND = 'splat.wav'
# The succes sound
TRILL_SOUND = 'trill.wav'


### JSON FILES ###

# The default level file
DEFAULT_LEVEL  = 'easy2.json'
# The object data (hitboxes) file
OBJECT_DATA    = 'objects.json'


### USE COMMAND LINE ARGUMENTS TO CHANGE DEFAULT LEVEL FILE AND FROG SPEED
"""
sys.argv is a list of the command line arguments when you run python. These arguments are
everything after the word python. So if you start the game typing

    python froggit default.json 1

Python puts ['froggit', 'default.json', '1'] into sys.argv. Below, we take advantage of
this fact to change the constant DEFAULT_LEVEL. This is the level file to be used when
you start the game.

The second argument is the FROG_SPEED, which is the amount of time between move steps.
A large value means a much slower moving frog.
"""
try:
    file = sys.argv[1]
    if file[-5:].lower() == '.json':
        DEFAULT_LEVEL = file
    else:
        DEFAULT_LEVEL = file+'.json'
except:
    pass # Use original value

try:
    value = float(sys.argv[2])
    FROG_SPEED = value
except:
    pass # Use original value


### ADD MORE CONSTANTS (PROPERLY COMMENTED) AS NECESSARY ###
