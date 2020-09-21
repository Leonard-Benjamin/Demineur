class ModelFactory(object):
	def __init__(self, model):
		self.model = model

	def get_model(self, line = 0, col = 0, bomb = 0):
		if self.model == "Demineur":
			from DemineurModel import DemineurModel
			return DemineurModel(lines=line, cols=col, bombs=bomb)
		elif self.model == "BTD":
			from BinaryThreeDungeonModel import BinaryThreeDungeonModel
			return BinaryThreeDungeonModel(lines=line, cols=col)
		elif self.model == "Sudoku":
			from SudokuModel import SudokuModel
			return SudokuModel()
		elif self.model == "Tetris":
			from TetrisModel import TetrisModel
			return TetrisModel()