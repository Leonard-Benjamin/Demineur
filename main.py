from Client import start
from Constants import *

if __name__ == "__main__":
	line = int(sys.argv[1])
	col = int(sys.argv[2])
	bomb = int(sys.argv[3])
	start(line, col, bomb)