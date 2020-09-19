from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from collections import deque
import sys
import time

from Constants import *

from GridManager import  GridManager
from BinaryTreeDungeon2 import *
from noise_gen import NoiseGen

class Model(object):

    def __init__(self, line = None, col = None, bomb = None):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        self.grid = []

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self.grid = []
        if line is not None:
        	self.lines = line
        else:
        	self.lines = LINES_COUNT
        if col is not None:
        	self.columns = col
        else:
        	self.columns = COLUMNS_COUNT
        if bomb is not None:
        	self.bombs = bomb
        else:
        	self.bombs = BOMBS_COUNT

        self._initialize()

    def get_grid_center(self):
    	print(str(self.lines / 2) + str(self.columns / 2))
    	return int(self.lines / 2), int(self.columns / 2)

    def get_number_of_bombs(self):
    	return str(self.bombs)

    def get_number_of_cell_revealed(self):
    	return str(len([cell for line in self.grid for cell in line if cell.state == cell._REVEALED]))

    def get_number_of_cell_hidded(self):
    	return str(len([cell for line in self.grid for cell in line if cell.state == cell._HIDDED]))

    def gen_demineur(self, immediate = False, is_win=False):
        #if is_win:
        #    self.lines += 5
        #    self.columns += 5

        arena_min_line = - 15
        arena_min_col = - 15
        arena_max_line = self.lines + 15
        arena_max_col = self.columns + 15

        gm = GridManager()
        self.grid = gm.get_grid(self.lines, self.columns, self.bombs)

        for line in self.grid:
            for cell in line:
                self.add_block((cell.x, 0, cell.z), HIDED_CELL, immediate = immediate)
        for line in range(arena_min_line, arena_max_line + 1):
            for col in range(arena_min_col, arena_max_col + 1):
                if arena_min_line <= line <= arena_max_line and arena_min_col <= col <= arena_max_col: 
                    self.add_block((line, -1, col), ROOF, immediate = False)
                    if line == arena_max_line or line == arena_min_line or col == arena_max_col or col == arena_min_col:
                        for x in range(0, 3):
                            self.add_block((line, x, col), HIDED_CELL, immediate = False)
                    elif line == arena_max_line - 1 or line == arena_min_line + 1 or col == arena_max_col - 1 or col == arena_min_col + 1:
                        for x in range(0, 2):
                            self.add_block((line, x, col), HIDED_CELL, immediate = False)
                    elif line == arena_max_line - 2 or line == arena_min_line + 2 or col == arena_max_col - 2 or col == arena_min_col + 2:
                        for x in range(0, 1):
                            self.add_block((line, x, col), HIDED_CELL, immediate = False)

    def _initialize(self):
        """ Initialize the world by placing all the blocks.
        """

        n = 124  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        
        #Demineur gen
        self.gen_demineur()

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def reveal_arround(self, cell):
    	for line in range(cell.x - 1, cell.x + 2):
    		for col in range(cell.z - 1, cell.z + 2):
    			if 0 <= line < self.lines and 0 <= col < self.columns:
    				curr_cell = self.grid[line][col]
    				if curr_cell.state == curr_cell._HIDDED:
    					self.reveal(curr_cell, (line, 0, col))

    def reveal(self, cell, block):
        cell.state = cell._REVEALED
        print(str(cell.number_arround))
        if cell.number_arround == 0:
            self.reveal_arround(cell)
            self.add_block(block, EMPTY)
        elif cell.number_arround == 1:
            self.add_block(block, ONE)
        elif cell.number_arround == 2:
            self.add_block(block, TWO)
        elif cell.number_arround == 3:
            self.add_block(block, THREE)
        elif cell.number_arround == 4:
            self.add_block(block, FOUR)
        elif cell.number_arround == 5:
            self.add_block(block, FIVE)
        elif cell.number_arround == 6:
            self.add_block(block, SIX)
        elif cell.number_arround == 7:
            self.add_block(block, SEVEN)
        elif cell.number_arround == 8:
            self.add_block(block, EIGHT)

    def display_bombs(self):
        for line in self.grid:
            for cell in line:
                if cell.is_bomb:
                    if cell.state == cell._REVEALED:
                        self.add_block((cell.x, 0, cell.z), HIDED_CELL)
                        cell.state = cell._HIDDED
                    else:
                        self.add_block((cell.x, 0, cell.z), BOMB)
                        cell.state = cell._REVEALED 

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.
        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.
        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.
        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.
        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.
        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.process_time()
        while self.queue and time.process_time() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.
        """
        while self.queue:
            self._dequeue()
