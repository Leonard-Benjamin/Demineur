class BaseCell(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class Cell(BaseCell):

	_REVEALED = 1
	_HIDDED = 2

	def __init__(self, x, y, z, number_arround, is_bomb):
		super(Cell, self).__init__(x, y, z)
		self.number_arround = number_arround
		self.is_bomb = is_bomb
		self.state = self._HIDDED
		self.flagged = False

class SudokuCell(BaseCell):

	def __init__(self, x, y, z, region, number):
		super(SudokuCell, self).__init__(x, y, z)
		self.region = region
		self.number = number
		self.possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]

	def remove_possibility(self, possibility):
		if possibility in self.possible_values:
			self.possible_values.remove(possibility)

	def add_possibility(self, possibility):
		if not possibility in self.possible_values:
			self.possible_values.append(possibility)
			self.possible_values = sorted(self.possible_values)

	def set_value(self, value):
		self.number = value
		self.remove_possibility(value)

	def remove_value(self, value):
		self.number = 0
		if value not in self.possible_values:
			self.add_possibility(value)