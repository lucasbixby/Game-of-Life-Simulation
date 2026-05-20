from config import MATRIX_LEN
import time



class Cell:
    def __init__(self, row: int, col: int):
        # all cells should have a position row, col and a status value
        self.row = row
        self.col = col
        self.status = 0
        listeners = []

    def __str__(self) -> str:
        # string representation of the cell 
        return str(self.status)

    def toggle_cell_status(self):
        # switches value of cell (alive or dead)
        self.status = 1 - self.status


class Board:
    # board class for storing the cells  

    def __init__(self, size) -> None:
        # board constructor
        self.matrix = self.build_grid(size)

    def __str__(self) -> str:
        # creates a string representation of the board 
        matrix_str = ""
        for row in self.matrix:
            row_str = ""
            for cell in row:
                row_str += f"{cell.status} "
            matrix_str += row_str + "\n"
        return matrix_str

    def build_grid(self, MATRIX_LEN) -> list[list[object]]:
        # assembles grid with cells
        matrix = []
        for i in range(MATRIX_LEN):
            row = []
            for k in range(MATRIX_LEN):
                row.append(Cell(i, k))
            matrix.append(row)
        return matrix

    def clear_board(self):
        # resets all cells to 0 
        for i in range(len(self.matrix)):
            for k in range(len(self.matrix[i])):
                self.matrix[i][k].status = 0

    def count_live_neighbors(self, row: int, col: int) -> int:
        # FIXME personalize and understand the code
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        live_neighbors = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < MATRIX_LEN and 0 <= c < MATRIX_LEN:  # Ensure within bounds
                live_neighbors += self.matrix[r][c].status  # Count alive neighbors

        return live_neighbors

    def update_classic(self) -> bool:
        # FIXME simplify expression
        new_matrix = [[Cell(i, j) for j in range(MATRIX_LEN)] for i in range(MATRIX_LEN)]
        changed = False  # Track if any cell changes state

        for i in range(MATRIX_LEN):
            for j in range(MATRIX_LEN):
                live_neighbors = self.count_live_neighbors(i, j)
                if self.matrix[i][j].status == 1:
                    new_matrix[i][j].status = 1 if live_neighbors in [2, 3] else 0
                else:
                    new_matrix[i][j].status = 1 if live_neighbors == 3 else 0

                # Check if the status has changed
                if new_matrix[i][j].status != self.matrix[i][j].status:
                    changed = True  # At least one cell changed

        self.matrix = new_matrix  # Update the board state
        return changed  # Return True if changes happened, False otherwise


class listener(object):
    def __init__(self):
        pass


def main():

    display_board = Board(MATRIX_LEN)
    # FIXME
    # create a way to preset boards
    display_board.matrix[0][2].toggle_cell_status()
    display_board.matrix[1][0].toggle_cell_status()
    display_board.matrix[2][1].toggle_cell_status()
    display_board.matrix[2][2].toggle_cell_status()
    display_board.matrix[1][2].toggle_cell_status()

    rule = "classic"

    if rule == "classic":
        print(display_board)

        while display_board.update_classic():
            time.sleep(.5)
            print(display_board)


if __name__ == "__main__":
    main()