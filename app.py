import streamlit as st
import time

# ── Config ────────────────────────────────────────────────────────────────────
MATRIX_LEN = 50
CELL_SIZE   = 12          # pixels per cell in the SVG canvas

# ── Domain classes (unchanged logic from main.py) ─────────────────────────────

class Cell:
    def __init__(self, row: int, col: int):
        self.row    = row
        self.col    = col
        self.status = 0

    def toggle_cell_status(self):
        self.status = 1 - self.status


class Board:
    def __init__(self, size: int):
        self.size   = size
        self.matrix = self._build_grid()

    def _build_grid(self):
        return [[Cell(i, k) for k in range(self.size)] for i in range(self.size)]

    def clear_board(self):
        for row in self.matrix:
            for cell in row:
                cell.status = 0

    def count_live_neighbors(self, row: int, col: int) -> int:
        directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        count = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                count += self.matrix[r][c].status
        return count

    def update_classic(self) -> bool:
        new_matrix = [[Cell(i, j) for j in range(self.size)] for i in range(self.size)]
        changed = False
        for i in range(self.size):
            for j in range(self.size):
                n = self.count_live_neighbors(i, j)
                if self.matrix[i][j].status == 1:
                    new_matrix[i][j].status = 1 if n in (2, 3) else 0
                else:
                    new_matrix[i][j].status = 1 if n == 3 else 0
                if new_matrix[i][j].status != self.matrix[i][j].status:
                    changed = True
        self.matrix = new_matrix
        return changed

    def any_alive(self) -> bool:
        return any(self.matrix[r][c].status == 1
                   for r in range(self.size)
                   for c in range(self.size))


# ── Session-state helpers ─────────────────────────────────────────────────────

def init_state():
    if "board" not in st.session_state:
        st.session_state.board            = Board(MATRIX_LEN)
        st.session_state.last_alive_step  = [[None]*MATRIX_LEN for _ in range(MATRIX_LEN)]
        st.session_state.step             = 0
        st.session_state.running          = False


def cell_color(row: int, col: int) -> str:
    board           = st.session_state.board
    last_alive_step = st.session_state.last_alive_step
    step            = st.session_state.step

    if board.matrix[row][col].status == 1:
        return "#111111"        # alive → near-black

    last = last_alive_step[row][col]
    if last is None:
        return "#f8f8f8"        # never been alive

    dt = step - last
    if dt == 1:  return "#ef4444"   # red
    if dt == 2:  return "#f97316"   # orange
    if dt == 3:  return "#facc15"   # yellow
    return "#f8f8f8"


def sync_last_alive():
    """After a board update, refresh last_alive_step for any living cells."""
    for r in range(MATRIX_LEN):
        for c in range(MATRIX_LEN):
            if st.session_state.board.matrix[r][c].status == 1:
                st.session_state.last_alive_step[r][c] = st.session_state.step


def do_step():
    st.session_state.step += 1
    st.session_state.board.update_classic()
    sync_last_alive()


# ── SVG grid renderer ─────────────────────────────────────────────────────────

def render_svg() -> str:
    size   = MATRIX_LEN
    cs     = CELL_SIZE
    width  = size * cs
    height = size * cs

    rects = []
    for r in range(size):
        for c in range(size):
            x     = c * cs
            y     = r * cs
            color = cell_color(r, c)
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                f'fill="{color}" stroke="#d1d5db" stroke-width="0.3"/>'
            )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        + "".join(rects)
        + "</svg>"
    )


# ── Preset patterns ───────────────────────────────────────────────────────────

PRESETS = {
    "Glider": [(0,2),(1,0),(2,1),(2,2),(1,2)],
    "Blinker": [(5,4),(5,5),(5,6)],
    "Pulsar": [
        (2,4),(2,5),(2,6),(2,10),(2,11),(2,12),
        (4,2),(4,7),(4,9),(4,14),
        (5,2),(5,7),(5,9),(5,14),
        (6,2),(6,7),(6,9),(6,14),
        (7,4),(7,5),(7,6),(7,10),(7,11),(7,12),
        (9,4),(9,5),(9,6),(9,10),(9,11),(9,12),
        (10,2),(10,7),(10,9),(10,14),
        (11,2),(11,7),(11,9),(11,14),
        (12,2),(12,7),(12,9),(12,14),
        (14,4),(14,5),(14,6),(14,10),(14,11),(14,12),
    ],
    "R-pentomino": [(1,2),(1,3),(2,1),(2,2),(3,2)],
}

def load_preset(name: str):
    st.session_state.board           = Board(MATRIX_LEN)
    st.session_state.last_alive_step = [[None]*MATRIX_LEN for _ in range(MATRIX_LEN)]
    st.session_state.step            = 0
    offset_r, offset_c = 10, 10
    for (r, c) in PRESETS[name]:
        st.session_state.board.matrix[r + offset_r][c + offset_c].status = 1
    sync_last_alive()


# ── Page layout ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Conway's Game of Life", layout="centered")
init_state()

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  h1 { font-family: 'Courier New', monospace; letter-spacing: 0.05em; }
  .stButton > button {
    font-family: 'Courier New', monospace;
    border-radius: 2px;
    font-size: 0.85rem;
  }
</style>
""", unsafe_allow_html=True)

st.title("Conway's Game of Life")
st.caption("Color trail: **black** = alive · **red** = died 1 step ago · **orange** = 2 · **yellow** = 3")

# ── Controls ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    step_btn = st.button("⏭ Step")

with col2:
    run_label = "⏸ Pause" if st.session_state.running else "▶ Run"
    toggle_btn = st.button(run_label)

with col3:
    clear_btn = st.button("🗑 Clear")

with col4:
    speed = st.select_slider("Speed", options=["Slow", "Medium", "Fast"],
                             value="Medium", label_visibility="collapsed")

SPEED_MAP = {"Slow": 0.5, "Medium": 0.25, "Fast": 0.1}

# ── Preset row ────────────────────────────────────────────────────────────────
st.markdown("**Presets:**")
pcols = st.columns(len(PRESETS))
for idx, name in enumerate(PRESETS):
    with pcols[idx]:
        if st.button(name, key=f"preset_{name}"):
            load_preset(name)
            st.session_state.running = False

# ── Handle control buttons ────────────────────────────────────────────────────
if step_btn:
    do_step()
    st.session_state.running = False

if toggle_btn:
    st.session_state.running = not st.session_state.running

if clear_btn:
    st.session_state.board.clear_board()
    st.session_state.last_alive_step = [[None]*MATRIX_LEN for _ in range(MATRIX_LEN)]
    st.session_state.step = 0
    st.session_state.running = False

# ── Draw grid ─────────────────────────────────────────────────────────────────
grid_placeholder = st.empty()
grid_placeholder.image(render_svg().encode(), use_container_width=True)

# ── Step info ─────────────────────────────────────────────────────────────────
alive_count = sum(
    st.session_state.board.matrix[r][c].status
    for r in range(MATRIX_LEN) for c in range(MATRIX_LEN)
)
st.markdown(f"**Step:** {st.session_state.step} &nbsp;|&nbsp; **Alive cells:** {alive_count}")

# ── Draw-on-grid note ─────────────────────────────────────────────────────────
st.info(
    "💡 **To draw cells:** use the presets above, or click **Step** / **Run** after a preset loads. "
    "For freehand drawing, run locally with `python graphics.py` (uses the original tkinter UI).",
    icon=None,
)

# ── Auto-run loop ─────────────────────────────────────────────────────────────
if st.session_state.running:
    if st.session_state.board.any_alive():
        time.sleep(SPEED_MAP[speed])
        do_step()
        st.rerun()
    else:
        # Fade 3 extra steps then stop
        for _ in range(3):
            time.sleep(SPEED_MAP[speed])
            st.session_state.step += 1
            sync_last_alive()
        st.session_state.running = False
        st.rerun()
