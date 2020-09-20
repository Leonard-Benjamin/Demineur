from Model import Model
import itertools
from Constants import *
from SudokuManager import SudokuManager

class SudokuModel(Model):
	def __init__(self, **kwargs):
		super(SudokuModel, self).__init__(**kwargs)

	def _initialize(self):
		self.gen_sudoku_model()

	def setup(self, **kwargs):
		pass

	def add_block(self, position, texture, immediate= True):
		super(SudokuModel, self).add_block(position, texture, immediate)

	def reveal(self, cell):
		block = (cell.x, cell.y, cell.z)
		if cell.number == 1:
			self.add_block(block, ONE)
		elif cell.number == 2:
			self.add_block(block, TWO)
		elif cell.number == 3:
			self.add_block(block, THREE)
		elif cell.number == 4:
			self.add_block(block, FOUR)
		elif cell.number == 5:
			self.add_block(block, FIVE)
		elif cell.number == 6:
			self.add_block(block, SIX)
		elif cell.number == 7:
			self.add_block(block, SEVEN)
		elif cell.number == 8:
			self.add_block(block, EIGHT)
		elif cell.number == 9:
			self.add_block(block, NINE)
		else:
			self.add_block(block, HIDED_CELL)

	def gen_sudoku_model(self):
		sm = SudokuManager()
		sm.gen_sudoku()
		grid = sm.grid
		for line in grid:
			text = ""
			for cell in line:
				text += "({}, {})".format(str(len(cell.possible_values)), str(cell.number))
				self.reveal(cell)
			print(text)