from Model import Model
from Constants import *
import os

class TetrisModel(Model):
	def __init__(self, **kwargs):
		super(TetrisModel, self).__init__(**kwargs)

	def setup(self, **kwargs):
		pass

	def _initialize(self):
		schema = self.load_tetris_schema()
		self.construct_tetris(schema)

	def add_block(self, position, texture, immediate= True):
		super(TetrisModel, self).add_block(position, texture, immediate)

	def load_tetris_schema(self):
		board = []
		with open("tetris.txt", "r") as tetris_schema:
			for line in tetris_schema.readlines():
				board.append(line)
			tetris_schema.close()
		return board

	def construct_tetris(self, schema):
		y = 0
		for line in schema:
			x = 0
			z = 0
			for char in line:
				if char == "#": 
					self.add_block((x, y, z), EMPTY)
				elif char == "*":
					self.add_block((x, y, z), FOUR)
				else:
					self.add_block((x, y, z), HIDED_CELL)
				z -= 1
			y -= 1
					
		