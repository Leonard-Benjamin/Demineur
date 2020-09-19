import sys
import math

TEXTURE_PATH = 'texture.png'
SECTOR_SIZE = 16

TICKS_PER_SEC = 60

# Size of sectors used to ease block loading.

# Movement variables
WALKING_SPEED = 10

MENU_PATH = "menu.png"

LINES_COUNT = 15
COLUMNS_COUNT = 15
BOMBS_COUNT = 20

FLYING_SPEED = 15
CROUCH_SPEED = 2
SPRINT_SPEED = 7
SPRINT_FOV = SPRINT_SPEED / 2

GRAVITY = 25
JUMP_GRAVITY = 10
MAX_JUMP_HEIGHT = 1.5 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * JUMP_GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

# Player variables
PLAYER_HEIGHT = 2
PLAYER_FOV = 80.0

if sys.version_info[0] >= 3:
    xrange = range

def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.
    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)

HIDED_CELL = tex_coords((0, 0), (0, 0), (0, 0))
BOMB = tex_coords((3, 0), (3, 0), (3, 0)) # Bas ->
FLAG = tex_coords((2, 0), (2, 0), (2, 0))
RESET = tex_coords((1, 2), (1, 2), (1, 2))
EMPTY = tex_coords((3, 2), (3, 2), (3, 2))
ROOF = tex_coords((2, 2), (2, 2), (2, 2))

ONE = tex_coords((0, 1), (0, 1), (0, 1))
TWO = tex_coords((0, 3), (0, 3), (0, 3))
THREE = tex_coords((2, 1), (2, 1), (2, 1))
FOUR = tex_coords((3, 1), (3, 1), (3, 1))
FIVE = tex_coords((0, 2), (0, 2), (0, 2))
SIX = tex_coords((1, 3), (1, 3), (1, 3))
SEVEN = tex_coords((2, 3), (2, 3), (2, 3))
EIGHT = tex_coords((3, 3), (3, 3), (3, 3))
