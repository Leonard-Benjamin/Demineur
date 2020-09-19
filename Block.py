class Block(object):
	name = ""
	texture = None

	def __init__(self, texture, name, position):
		self.texture = texture
		self.name = name
		self.position = position
