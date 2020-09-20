from Model import Model
from BinaryTreeDungeon2 import *
from Constants import *

class BinaryThreeDungeonModel(Model):
	def __init__(self, **kwargs):
		super(BinaryThreeDungeonModel, self).__init__(**kwargs)

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

	def _initialize(self, **kwargs):
		self.gen_binary_three_dungeon()

	def add_block(self, position, texture, immediate= True):
		super(BinaryThreeDungeonModel, self).add_block(position, texture, immediate)

	def gen_binary_three_dungeon(self):
		btd = BinaryTreeDungeon(self.lines, self.columns, False)
		finals = btd.root.get_finals()

		for final in finals:
			for line in range(final.lines):
				for col in range(final.columns):
					if final.weight > BLOCK_LINES * BLOCK_COLUMN:
						if not (line == 0 or line == final.lines - 1 or col == 0 or col == final.columns - 1):
							self.add_block((final.start_line + line, -1, final.start_column + col), EMPTY, immediate = True)
							self.add_block((final.start_line + line, 3, final.start_column + col), HIDED_CELL, immediate = True)
						else:
							self.add_block((final.start_line + line, -1, final.start_column + col), HIDED_CELL, immediate = True)
							self.add_block((final.start_line + line, 0, final.start_column + col), EMPTY, immediate = True)
							self.add_block((final.start_line + line, 1, final.start_column + col), EMPTY, immediate = True)
							self.add_block((final.start_line + line, 2, final.start_column + col), EMPTY, immediate = True)
							self.add_block((final.start_line + line, 3, final.start_column + col), EMPTY, immediate = True)