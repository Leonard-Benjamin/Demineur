import Block
from Constants import *

class OneBlock(Block):

	def __init__(self, position):
		super(Block, self).__init__(ONE, position, "OneBlock")
