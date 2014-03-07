from retrogamelib.gameobject import Group


WIN_SIZE = WWIDTH, WHEIGHT = 640, 480;
FPS = 60.;
CAPTION = "Platformer"


# Resources #
FONT_DIR = "./resources/fonts/"
IMAGE_DIR= "./resources/images/"
SOUND_DIR= "./resources/sounds/"
MAP_DIR  = "./resources/maps/"


snowfg_sprites_list = Group()
snowbg_sprites_list = Group()
tilebg_sprites_list = Group()
tilemg_sprites_list = Group()
tile_sprites_list = Group()
tilefg_sprites_list = Group()
enemy_sprites_list = Group()
player_sprites_list = Group()
bullet_sprites_list = Group()
fog_sprites_list = Group()
all_sprites_list = Group()


all_groups_list = [
                    all_sprites_list,
                    snowbg_sprites_list,
                    tilebg_sprites_list,
                    
                    tilemg_sprites_list,
                    player_sprites_list,
                    enemy_sprites_list,
                    bullet_sprites_list,
                    
                    tilefg_sprites_list,
                    snowfg_sprites_list
                  ]

STORY = {'intro.txt': ["Hello!",
                        "I am R458 Model 71MM1!",
                        "...or TIMMI for short :)",
                        "You can enter more text in constants.py!",]
        }
