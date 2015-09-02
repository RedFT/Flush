from entities import Tile
from constants import SCALE, MAP_DIR
from bs4 import BeautifulSoup


def load_map(filename, layer_name, collidable=True):
    """ returns a list of tiles placed based on tmx (xml) file """
    f = open(MAP_DIR + filename, "r")
    soup = BeautifulSoup(f, "xml")
    f.close()

    # parse file and retrieve values
    mwidth = int(soup.map.layer['width'])
    mheight = int(soup.map.layer['height'])
    twidth = int(soup.map.tileset["tilewidth"])
    theight = int(soup.map.tileset["tileheight"])
    tsetwidth = int(soup.map.tileset.image['width']) / twidth
    tsetheight = int(soup.map.tileset.image['height']) / theight
    map_csv = soup.map.find(attrs={'name': layer_name}).data.string.split(',')

    x, y = 0, 0

    if not map_csv:
        print "No Layer with name: %s" % layer_name
        return

    # generate and store tiles
    tiles_list = []
    for num in map_csv:
        px = x % mwidth
        py = x / mwidth
        num_i = int(num)
        tx = (num_i - 1) % tsetwidth
        ty = (num_i - 1) / tsetheight

        x += 1
        if num_i == 0:
            continue

        tile = Tile("TestTiles.png",
                    (px * twidth, py * theight),
                    (twidth, theight),
                    (tx * twidth, ty * theight))
        tiles_list.append(tile)
        if not collidable:
            tile.collidable = False
    return tiles_list
