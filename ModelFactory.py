class ModelFactory(object):

	bombs = "bomb"
	lines = "line"
	cols = "col"

	def __init__(self, model):
		self.model = model

	def get_model(self, lines, cols, bombs):
		if self.model == "Demineur":
			from DemineurModel import DemineurModel
			return DemineurModel(lines=lines, cols=cols, bombs=bombs)
		elif self.model == "BTD":
			from BinaryThreeDungeonModel import BinaryThreeDungeonModel
			return BinaryThreeDungeonModel(lines=lines, cols=cols)
		elif self.model == "Sudoku":
			from SudokuModel import SudokuModel
			return SudokuModel()
		elif self.model == "Tetris":
			from TetrisModel import TetrisModel
			return TetrisModel()