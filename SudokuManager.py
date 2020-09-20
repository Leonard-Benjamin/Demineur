from Cell import SudokuCell
import random

class SudokuManager(object):

	max_lines = 9
	max_cols = 9
	max_regions = 9
	max_number = 9
	grid = []

	def __init__(self):
		pass

	def determine_region(self, x, z):
		if x in range(0, 3):
			if z in range(0, 3):
				return 0
			if z in range(3, 6):
				return 1
			if z in range(6, 9):
				return 2
		if x in range(3, 6):
			if z in range(0, 3):
				return 3
			if z in range(3, 6):
				return 4
			if z in range(6, 9):
				return 5
		if x in range(6, 9):
			if z in range(0, 3):
				return 6
			if z in range(3, 6):
				return 7
			if z in range(6, 9):
				return 8

	def display(self, raw):
		print(str(raw))

	def has_duplicate(self, raw):
		c = {}
		for val in raw:
			if val in c and val != 0:
				return True
			c[val] = True
		return False

	def is_valid(self, grid):
		'''for i in range(9):
			if (self.has_duplicate([cell.number for line in grid for cell in line if cell.x == i and cell.number != 0]) or
				self.has_duplicate([cell.number for line in grid for cell in line if cell.z == i and cell.number != 0]) or
				self.has_duplicate([cell.number for line in grid for cell in line if cell.region == i and cell.number != 0])):
				return False
		return True

		'''# Check raws and columns 
		for line in range(0, self.max_lines):
			raw_line = []
			raw_col = []
			for col in range(0, self.max_cols):
				raw_line.append(grid[line][col].number)
				raw_col.append(grid[col][line].number)
				raw_line = [value for value in raw_line if value != 0]
				raw_col = [value for value in raw_col if value != 0]

			if len(raw_line) != len(set(raw_line)) or len(raw_col) != len(set(raw_col)):
				return False

		#Check regions
		for region in range(self.max_regions):
			region_raw = [cell.number for line in grid for cell in line if cell.region == region and cell.number != 0]
			if len(region_raw) != len(set(region_raw)):
				return False

		return True

	def gen_sudoku(self):
		self.grid = self.solve(self.gen_empty_grid())
		self.display_grid()
		return self.grid

	def display_grid(self):
		for region in range(self.max_regions):
			region_raw = [cell.number for line in self.grid for cell in line if cell.region == region]

		for line in self.grid:
			text = ""
			for cell in line:
				if cell.region == 8:
					text += (str(cell.number))
			if text != "":
				print(text)

	def get_random(self, max):
		return random.randint(0, max)

	def first_empty_cell(self, grid):
		for line in grid:
			for cell in line:
				if cell.number == 0:
					return cell.x, cell.z

	def random_first_empty_cell(self, grid):
		line = self.get_random(self.max_lines - 1)
		col = self.get_random(self.max_cols - 1)
		if grid[line][col].number == 0:
			return line, col
		else:
			return self.first_empty_cell(grid)


	def handle_possibility_in_line_col_region(self, grid, value, pos, set_value = True):
		if set_value:
			grid[pos[0]][pos[1]].set_value(value)
		else:
			grid[pos[0]][pos[1]].remove_value(value)
		for line in range(0, self.max_lines):
			for col in range(0, self.max_cols):
				if line == pos[0] or col == pos[1] or grid[line][col].region == grid[pos[0]][pos[1]].region:
					if set_value:
						grid[line][col].number(value)
					else:
						grid[line][col].add_possibility(value)
		return grid

	def is_complete(self, grid):
		return all(all(val.number != 0 for val in row) for row in grid)

	def solve(self, grid):
		if self.is_complete(grid):
			return grid
		r, c = self.first_empty_cell(grid)
		for i in range(1, 10):
			grid[r][c].number = i
			if self.is_valid(grid):
				result = self.solve(grid)
				if self.is_complete(result):
					return result
			grid[r][c].number = 0
		return grid

	def place_number(self, grid):
		number = self.get_random(self.max_lines) 
		x = self.get_random(self.max_lines - 1)
		z = self.get_random(self.max_lines - 1)
		if grid[x][z] and grid[x][z].number == 0:
			grid[x][z].number = number
			if not self.is_valid(grid):
				grid[x][z].number = 0
				for i in range(1, self.max_lines):
					grid[x][z].number = i
					if not self.is_valid(grid):
						grid[x][z].number = 0
					else:
						return grid
				return self.place_number(grid)
			else: 
				return grid
		else:
			return self.place_number(grid)

	def gen_empty_grid(self):
		listoflists = []
		for i in range(0, self.max_lines):
			sublist = []
			for j in range(0, self.max_cols):
				sublist.append(SudokuCell(i, 0, j, self.determine_region(i, j), 0))
			listoflists.append(sublist)
		return listoflists