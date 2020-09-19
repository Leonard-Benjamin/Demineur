import Block
from Constants import *

class TwoBlock(Block):

	def __init__(self, position):
		super(Block, self).__init__(BOMB, position, "TwoBlock")
