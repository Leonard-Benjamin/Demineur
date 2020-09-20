from Client import start
from Constants import *

if __name__ == "__main__":
	model = str(sys.argv[1])
	if model != "Sudoku" and not model == "Tetris":
		line = int(sys.argv[2])
		col = int(sys.argv[3])
		if model == "Demineur":
			bomb = int(sys.argv[4])
			start(model, line, col, bomb)
		elif model == "BTD":
			start(model, line, col)
	elif model == "Sudoku":
		start(model)
	elif model == "Tetris":
		start(model)