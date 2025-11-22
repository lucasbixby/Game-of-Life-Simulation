
class Cell(object):
    def __init__(self, row: int, col: int):
        # all cells should have a position row, col (0 -> len(matrix))
        self.row = row
        self.col = col
        self.status = False 
        listeners = []

    def __str__(self):
        return f"(row:{self.row}, col:{self.col})"

    def __repr__(self):
        return f"Cell({self.row},{self.col})"
    