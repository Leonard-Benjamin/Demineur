import Block
from Constants import *

class BombBlock(Block):

	def __init__(self, position):
		super(Block, self).__init__(BOMB, position, "BombBlock")
