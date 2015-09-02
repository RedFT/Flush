import os

WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = 640, 480
FPS = 60.
CAPTION = "Platformer"
SCALE = 4


# Resources #
FONT_DIR = os.path.join("resources", "fonts") + "/"
IMAGE_DIR = os.path.join("resources", "images") + "/"
SOUND_DIR = os.path.join("resources", "sounds") + "/"
MAP_DIR = os.path.join("resources", "maps") + "/"

STORY = {'intro.txt': ["Hello!",
                       "I am R458 Model 71MM1!",
                       "...or TIMMI for short :)",
                       "You can enter more text in constants.py!", ]
         }
