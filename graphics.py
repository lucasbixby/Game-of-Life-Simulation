import tkinter as tk

from config import MATRIX_LEN
from main import Board  


class GameOfLifeGUI(tk.Frame):
    def __init__(self, master=None, size=MATRIX_LEN, cell_size=12):
        super().__init__(master)
        self.master = master
        self.size = size
        self.cell_size = cell_size

        # Game state
        self.board = Board(size)
        self.running = False

        # Step counter for “recently dead” colors
        self.step = 0
        # last_alive_step[row][col] = step number when the cell was last alive
        self.last_alive_step = [
            [None for _ in range(self.size)] for _ in range(self.size)
        ]

        # How many “extra” fade-only steps to run after all cells are dead
        self.post_termination_steps = 0

        # Build UI
        self._build_widgets()
        self._create_grid()
        self._update_canvas_from_board()

    def _build_widgets(self):
        # Canvas for the grid
        self.canvas = tk.Canvas(
            self.master,
            width=self.size * self.cell_size,
            height=self.size * self.cell_size,
            bg="white",
        )
        self.canvas.pack(padx=10, pady=10)

        # Click to toggle cells
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Click and drag to paint alive cells
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

        # Button row
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="Start", command=self.toggle_run)
        self.start_btn.pack(side="left", padx=5)

        self.step_btn = tk.Button(btn_frame, text="Step", command=self.step_once)
        self.step_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_board)
        self.clear_btn.pack(side="left", padx=5)

    def _create_grid(self):
        """Create rectangles for each cell and store their IDs."""
        self.rectangles = {}  # (row, col) -> rectangle id

        for row in range(self.size):
            for col in range(self.size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                rect_id = self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="gray",
                    fill="white",
                )
                self.rectangles[(row, col)] = rect_id

    # ---------- Interaction ----------

    def on_canvas_click(self, event):
        """Toggle the clicked cell between alive (1) and dead (0)."""
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if 0 <= row < self.size and 0 <= col < self.size:
            cell = self.board.matrix[row][col]
            old_status = cell.status
            cell.toggle_cell_status()
            new_status = cell.status

            # If user turns a cell on, treat it as alive at the current step
            if new_status == 1:
                self.last_alive_step[row][col] = self.step
            # If turned off manually, we don't mark it as "recently dead"
            # (no rule step happened), so it'll just draw as white.

            self._update_cell_color(row, col)

    def on_canvas_drag(self, event):
        """Paint cells alive while dragging with left mouse button."""
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if 0 <= row < self.size and 0 <= col < self.size:
            cell = self.board.matrix[row][col]
            if cell.status == 0:
                cell.status = 1
                # Newly painted alive → record as alive at current step
                self.last_alive_step[row][col] = self.step
                self._update_cell_color(row, col)

    # ---------- Coloring logic ----------

    def _get_cell_color(self, row, col):
        """
        Decide the color of a cell based on:
        - current status (alive/dead)
        - when it was last alive.
        """
        status = self.board.matrix[row][col].status

        if status == 1:
            # Alive now
            return "black"

        # Dead now — see how long ago it was alive
        last = self.last_alive_step[row][col]
        if last is None:
            return "white"

        dt = self.step - last
        if dt == 1:
            return "red"       # died on last step
        elif dt == 2:
            return "orange"    # died two steps ago
        elif dt == 3:
            return "yellow"    # died three steps ago
        else:
            return "white"     # older than 3 steps ago

    def _update_cell_color(self, row, col):
        """Update the color of a single cell on the canvas."""
        rect_id = self.rectangles[(row, col)]
        color = self._get_cell_color(row, col)
        self.canvas.itemconfig(rect_id, fill=color)

    def _update_canvas_from_board(self):
        """Refresh the entire grid to match the board state."""
        for (row, col), rect_id in self.rectangles.items():
            status = self.board.matrix[row][col].status

            # If it's alive now, update last_alive_step to this step
            if status == 1:
                self.last_alive_step[row][col] = self.step

            color = self._get_cell_color(row, col)
            self.canvas.itemconfig(rect_id, fill=color)

    def _any_alive(self):
        """Check if any cell in the board is currently alive."""
        for row in range(self.size):
            for col in range(self.size):
                if self.board.matrix[row][col].status == 1:
                    return True
        return False

    # ---------- Simulation control ----------

    def step_once(self):
        """
        Advance the simulation by one generation when user clicks 'Step'.
        (In auto-run, we use _run_loop instead, which also handles fade-only steps.)
        """
        # This is a true simulation step: update rules + colors
        self.step += 1
        self.board.update_classic()
        self._update_canvas_from_board()

    def _fade_step_only(self):
        """
        A 'fake' step after termination: no rule update, just bump the
        step counter so death-trail colors fade out.
        """
        self.step += 1
        self._update_canvas_from_board()

    def _run_loop(self):
        """Internal loop that keeps stepping while running is True."""
        if not self.running:
            return

        if self.post_termination_steps > 0:
            # We're in fade-only mode: no board update, just color decay
            self._fade_step_only()
            self.post_termination_steps -= 1

            if self.post_termination_steps > 0:
                self.master.after(200, self._run_loop)
            else:
                # Done fading; fully stopped
                self.running = False
                self.start_btn.config(text="Start")
        else:
            # Normal simulation step
            self.step += 1
            self.board.update_classic()
            self._update_canvas_from_board()

            if self._any_alive():
                # Keep running normally
                self.master.after(200, self._run_loop)
            else:
                # All cells dead → start 3 extra fade steps
                self.post_termination_steps = 3
                self.master.after(200, self._run_loop)

    def toggle_run(self):
        """Start or pause the continuous simulation."""
        if self.running:
            # Pause
            self.running = False
            self.start_btn.config(text="Start")
            # If we were mid-fade, cancel remaining fade steps
            self.post_termination_steps = 0
        else:
            # Start
            self.running = True
            self.start_btn.config(text="Pause")
            self._run_loop()

    def clear_board(self):
        """Reset all cells to dead and clear death history."""
        self.board.clear_board()
        self.last_alive_step = [
            [None for _ in range(self.size)] for _ in range(self.size)
        ]
        self.step = 0
        self.post_termination_steps = 0
        self._update_canvas_from_board()


def main():
    root = tk.Tk()
    root.title("Game of Life Simulation")
    app = GameOfLifeGUI(root, size=MATRIX_LEN, cell_size=12)
    root.mainloop()


if __name__ == "__main__":
    main()
