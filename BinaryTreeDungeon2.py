#encoding=utf-8

import random
import math

MIN_LINES = 4
MIN_COLUMNS = 4
BLOCK_LINES = 5
BLOCK_COLUMN = 5
MAX_COLUMNS = BLOCK_COLUMN * 2 + 1
MAX_LINES = BLOCK_LINES * 2 + 1


finals = []

class Leaf(object):
    start_line = None ## A x position in the Grid
    start_column = None ## A y position in the Grid
    lines = None ## Number of cell(s) in width
    columns = None ## Number of cell(s) in height
    left_Leaf = None
    right_leaf = None
    weight = None
    ok = False

    def __init__(self, start_line, start_column, lines, columns):
        self.start_column = start_column
        self.start_line = start_line
        self.lines = lines
        self.columns = columns
        self.weight = lines * columns

    def is_final_leaf(self):
        return not self.right_leaf and not self.left_Leaf

    def can_split(self):
        return self.lines - BLOCK_LINES >= BLOCK_LINES or self.columns - BLOCK_COLUMN >= BLOCK_COLUMN

    def is_correctly_sized(self):
        return self.lines <= MAX_LINES and self.columns <= MAX_COLUMNS

    def __repr__(self):
        return "Leaf start line : " + str(self.start_line) + "\n" + "Leaf start column : " + str(self.start_column) + "\n" + "Leaf lines : " + str(self.lines) + "\n" + "Leaf columns : " + str(self.columns)
        """logger.INFO("Leaf start line : " + str(self.start_line))
        logger.INFO("Leaf start column : " + str(self.start_column))
        logger.INFO("Leaf lines : " + str(self.lines))
        logger.INFO("Leaf columns : " + str(self.columns))"""

class IntermediateLeaf(Leaf):

    splitType = None

    def __init__(self, start_x, start_y, lines, columns, dont_split):
        super(IntermediateLeaf, self).__init__(start_x, start_y, lines, columns)
        if (not self.is_correctly_sized() and self.need_split() and not dont_split) or not self.ok:
            self.split()
        else: 
            if self.weight > BLOCK_COLUMN * BLOCK_LINES:
                finals.append(self)

    def vertical_split(self):
        ##split = random.randrange(BLOCK_COLUMN, stop=self.columns - BLOCK_COLUMN)
        try:
            split = random.randrange(BLOCK_COLUMN - 1, self.columns -BLOCK_COLUMN)
            assert(split >= 3), "Nombre de columns trop bas {}".format(str(split))
            self.left_Leaf = IntermediateLeaf(self.start_line, self.start_column, self.lines, split, False)
            self.right_leaf = IntermediateLeaf(self.start_line, self.start_column + split, self.lines, self.columns - split, False)
        except:
            finals.append(self)
            self.ok = True

    def horizontal_split(self):       
        try: 
            split = random.randrange(BLOCK_LINES - 1, self.lines - BLOCK_LINES)
            assert(split >= 3), "Nombre de columns trop bas {}".format(str(split))
            self.left_Leaf = IntermediateLeaf(self.start_line, self.start_column, split, self.columns, False)
            self.right_leaf = IntermediateLeaf(self.start_line + split, self.start_column, self.lines - split, self.columns, False)
        except:
            finals.append(self)
            self.ok = True

    def random_split(self):
        rand = random.randrange(100)
        if rand >= 51:
            self.vertical_split()
        else:
            self.horizontal_split()

    def need_split(self):
        return not self.ok and not float(max(self.columns, self.lines / 2) <= float(BLOCK_LINES))
        
    def split(self):
        if self.lines / self.columns > 1.2:
            self.horizontal_split()
            self.splitType = "H"
        elif self.columns / self.lines > 1.2:
            self.vertical_split()
            self.splitType =  "V"
        else:
            self.random_split()
            self.splitType = "R"

    def make_dungeon_leafs(self):
        self.split()

    def get_finals(self):
        return finals

class BinaryTreeDungeon:
    root = None

    def __init__(self, width, height, dont_split):
        self.root = IntermediateLeaf(0, 0, width, height, dont_split)

def draw_finals(lines, columns):
    grid = []
    for lines in range(lines):
        line = []
        for column in range(columns):
            line.append("O")
        grid.append(line)
    for final in finals:
        for line in range(final.lines):
            for col in range(final.columns):
                if final.weight > BLOCK_LINES * BLOCK_COLUMN:
                    if not (line == 0 or line == final.lines - 1 or col == 0 or col == final.columns - 1):
                        grid[final.start_line + line][final.start_column + col] = " "
    with open("./Map.txt", "w+") as gridFile:
        for line in grid:
            gridFile.write("".join(line) + "\n")
        gridFile.close()

if __name__=="__main__":
    lines = 25
    columns = 25
    btd = BinaryTreeDungeon(lines, columns, False)
    btd.root.finals_leafs()
    logger.INFO(str(len(finals)))
    for final in finals:
        logger.INFO(final.__repr__())

    grid = draw_finals(lines, columns)
    """for line in grid:
        print(line)"""
    with open("./Map.txt", "w+") as gridFile:
        for line in grid:
            gridFile.write("".join(line) + "\n")
        gridFile.close()