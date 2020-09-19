import math
import random
from Cell import Cell

class GridManager(object):

	grid = []
	max_lines = 0
	max_cols = 0
	number_of_bombs = 0

	def create_grid(self):
		listoflists = []
		for i in range(0, self.max_lines):
			sublist = []
			for j in range(0, self.max_cols):
				sublist.append(Cell(i, j, 0, False))
			listoflists.append(sublist)
		return listoflists

	def check_cell_exists(self, line, col, max_line, max_col):
		return (0 <= line < max_line) and (0 <= col < max_col)

	def place_bomb(self, line, col):
		self.grid[line][col].is_bomb = True

		for nline in range( line - 1, line + 2):
			for ncol in range(col - 1, col + 2):
				if self.check_cell_exists(nline, ncol, self.max_lines, self.max_cols):
					self.grid[nline][ncol].number_arround += 1

	def check_bomb(self):
		bomb_line = random.randint(0, self.max_lines - 1)
		bomb_col = random.randint(0, self.max_cols - 1)
		if self.grid[bomb_line][bomb_col].is_bomb:
			self.check_bomb()
		else:
			self.place_bomb(bomb_line, bomb_col)
			return True

	def palce_bombs(self):
		for bomb in range(0, self.number_of_bombs):
			self.check_bomb()

	def get_grid(self, line, col, bomb):
		self.max_lines = line
		self.max_cols = col
		self.number_of_bombs = bomb
		self.grid = self.create_grid()
		self.palce_bombs()
		return self.grid
