from Model import Model
from GridManager import GridManager
from Constants import *

class DemineurModel(Model):
	def __init__(self, **kwargs):
		super(DemineurModel, self).__init__(**kwargs)

	def setup(self, **kwargs):
		dic = kwargs
		if dic["lines"] is not None:
			self.lines = dic["lines"]
		else:
			self.lines = LINES_COUNT
		if dic["cols"] is not None:
			self.columns = dic["cols"]
		else:
			self.columns = COLUMNS_COUNT
		if dic["bombs"] is not None:
			self.bombs = dic["bombs"]
		else:
			self.bombs = BOMBS_COUNT

	def _initialize(self):
		self.gen_demineur()


	def gen_demineur(self, immediate = False, is_win=False):
		self.grid = []
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
						for x in range(2,3):
							self.add_block((line, x/2, col), HIDED_CELL, immediate = False)
					elif line == arena_max_line - 1 or line == arena_min_line + 1 or col == arena_max_col - 1 or col == arena_min_col + 1:
						for x in range(1, 2):
							self.add_block((line, x/2, col), HIDED_CELL, immediate = False)
					elif line == arena_max_line - 2 or line == arena_min_line + 2 or col == arena_max_col - 2 or col == arena_min_col + 2:
						for x in range(0, 1):
							self.add_block((line, x/2, col), HIDED_CELL, immediate = False)

	def reveal_arround(self, cell):
		for line in range(cell.x - 1, cell.x + 2):
			for col in range(cell.z - 1, cell.z + 2):
				if not (line==cell.x and col==cell.z) and 0 <= line < self.lines and 0 <= col < self.columns:
					curr_cell = self.grid[line][col]
					if curr_cell.state == curr_cell._HIDDED:
						self.reveal(curr_cell, (line, 0, col))

	def reveal(self, cell, block, debug = False):
		cell.state = cell._REVEALED
		if cell.number_arround == 0:
			if not debug:
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

	def display_non_bomb(self):
		for line in self.grid:
			for cell in line:
				if not cell.is_bomb:
					if cell.state == cell._REVEALED:
						self.add_block((cell.x, 0, cell.z), HIDED_CELL)
						cell.state = cell._HIDDED
					else:
						self.reveal(cell ,(cell.x, 0, cell.z), True)

	def get_grid_center(self):
		return int(self.lines / 2), int(self.columns / 2)

	def get_number_of_bombs(self):
		return str(self.bombs)

	def get_number_of_cell_revealed(self):
		return str(len([cell for line in self.grid for cell in line if cell.state == cell._REVEALED]))

	def get_number_of_cell_hidded(self):
		return str(len([cell for line in self.grid for cell in line if cell.state == cell._HIDDED]))