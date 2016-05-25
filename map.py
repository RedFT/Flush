from bs4 import BeautifulSoup

from constants import MAP_DIR
from ecs.entities.entities import Tile


def load_map(filename, layer_name, collidable=True):
    """ returns a list of tiles placed based on tmx (xml) file """
    f = open(MAP_DIR + filename, "r")
    soup = BeautifulSoup(f, "xml")
    f.close()

    # parse file and retrieve values
    map_width = int(soup.map.layer['width'])
    map_height = int(soup.map.layer['height'])
    tile_width = int(soup.map.tileset["tilewidth"])
    tile_height = int(soup.map.tileset["tileheight"])
    tileset_width = int(soup.map.tileset.image['width']) / tile_width
    tileset_height = int(soup.map.tileset.image['height']) / tile_height
    map_csv = soup.map.find(attrs={'name': layer_name}).data.string.split(',')

    x, y = 0, 0

    if not map_csv:
        print "No Layer with name: %s" % layer_name
        return

    # generate and store tiles
    tiles_list = []
    for num in map_csv:
        px = x % map_width
        py = x / map_width
        num_i = int(num)
        tx = (num_i - 1) % tileset_width
        ty = (num_i - 1) / tileset_height

        x += 1
        if num_i == 0:
            continue

        tile = Tile("TestTiles.png",
                    (px * tile_width, py * tile_height),
                    (tile_width, tile_height),
                    (tx * tile_width, ty * tile_height))
        tiles_list.append(tile)
        if not collidable:
            tile.collidable = False
    return tiles_list
