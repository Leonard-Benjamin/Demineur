class Cell(object):

	_REVEALED = 1
	_HIDDED = 2

	def __init__(self, x, z, number_arround, is_bomb):
		self.x = x
		self.z = z
		self.number_arround = number_arround
		self.is_bomb = is_bomb
		self.state = self._HIDDED
		self.flagged = False