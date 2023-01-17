"""
The primary application script for Froggit

This is the module with the application code.  Make sure that this module is
in a folder with the following files:

    app.py      (the primary controller class)
    level.py    (the subcontroller for a single game level)
    models.py   (the model classes)
    consts.py   (the application constants)

In addition, you should have the following subfolders

    Fonts         (fonts to use for GLabel)
    Sounds        (sound effects for the game)
    Images        (image files to use in the game)
    JSON          (json files with the game data)

Moving any of these folders or files will prevent the game from working properly

Author: Walker M. White (wmw2)
Date:   November 1, 2020
"""
from consts import *
from app import *

# Application code
if __name__ == '__main__':
    Froggit(width=GAME_WIDTH,height=GAME_HEIGHT).run()
