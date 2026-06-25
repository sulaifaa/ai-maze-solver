import tkinter as tk
from tkinter import messagebox, ttk

import maze_backend as backend   # ← the separated logic layer

# VISUAL CONSTANTS  (GUI-only, not needed by the backend)
ROWS        = backend.ROWS
COLS        = backend.COLS
CELL_SIZE   = 28
CELL_RADIUS = 7
CELL_GAP    = 4
CANVAS_PAD  = 16

BG_PAGE    = "#f0f0f7"
BG_SIDEBAR = "#ffffff"
BG_CANVAS  = "#e8e8f4"
BG_CARD    = "#ffffff"
BORDER_CARD = "#e2e2f0"

A_CORAL      = "#ff6b6b"
A_MINT       = "#00c9a7"
A_VIOLET     = "#7c5cbf"
A_VIOLET_DRK = "#6d28d9"
A_INDIGO     = "#4f46e5"
A_GOLD       = "#f59e0b"
A_WARM       = "#f97316"

CELL_EMPTY    = "#dcdcee"
CELL_WALL     = "#c084fc"
CELL_WALL_DRK = "#7e22ce"
CELL_VISITED  = "#bae6fd"
CELL_VIS_DRK  = "#38bdf8"
CELL_PATH     = "#818cf8"
CELL_PATH_DRK = "#4f46e5"
CELL_START    = "#6ee7b7"
CELL_START_DK = "#059669"
CELL_END      = "#fca5a5"
CELL_END_DK   = "#ef4444"

T_DARK = "#1e1b4b"
T_MID  = "#6b7280"
BTN_HVR = "#ede9fe"

FONT_SECTION = ("Helvetica", 8,  "bold")
FONT_BTN     = ("Helvetica", 10, "bold")
FONT_STATUS  = ("Helvetica", 9)
FONT_SMALL   = ("Helvetica", 8)

# derived canvas dimensions 
DRAW_W = COLS * (CELL_SIZE + CELL_GAP) + CELL_GAP
DRAW_H = ROWS * (CELL_SIZE + CELL_GAP) + CELL_GAP

# DRAW MODE  (GUI state, not grid/algorithm state)=
mode = "wall"

# ROOT WINDOW
root = tk.Tk()
root.title("MAZE.AI")
root.configure(bg=BG_PAGE)
root.resizable(False, False)

# HELPERS
def rounded_rect(cv, x1, y1, x2, y2, r, **kw):
    pts = [
        x1+r, y1,   x2-r, y1,
        x2,   y1,   x2,   y1+r,
        x2,   y2-r, x2,   y2,
        x2-r, y2,   x1+r, y2,
        x1,   y2,   x1,   y2-r,
        x1,   y1+r, x1,   y1,
    ]
    return cv.create_polygon(pts, smooth=True, **kw)


def card(parent, pady=(0, 10)):
    outer = tk.Frame(parent, bg=BORDER_CARD)
    outer.pack(fill="x", pady=pady)
    inner = tk.Frame(outer, bg=BG_CARD, padx=14, pady=12)
    inner.pack(fill="both", padx=1, pady=1)
    return inner


def section_lbl(parent, text):
    tk.Label(parent, text=text.upper(), fg=A_GOLD, bg=BG_CARD,
             font=FONT_SECTION).pack(anchor="w", pady=(0, 6))


def make_btn(parent, text, cmd, fg=A_VIOLET, bg=BG_CARD, ipady=7):
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                  activebackground=BTN_HVR, activeforeground=fg,
                  font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=BORDER_CARD)
    b.pack(fill="x", pady=2, ipady=ipady)
    b.bind("<Enter>",         lambda e: b.config(bg=BTN_HVR, highlightbackground=fg))
    b.bind("<Leave>",         lambda e: b.config(bg=bg,      highlightbackground=BORDER_CARD))
    b.bind("<ButtonPress-1>", lambda e: b.config(bg=fg, fg="#ffffff"))
    b.bind("<ButtonRelease-1>", lambda e: b.config(bg=BTN_HVR, fg=fg))
    return b

# HEADER
header = tk.Frame(root, bg=BG_SIDEBAR)
header.pack(fill="x")
hinner = tk.Frame(header, bg=BG_SIDEBAR, padx=22, pady=14)
hinner.pack(fill="x")

logo_fr = tk.Frame(hinner, bg=BG_SIDEBAR)
logo_fr.pack(side="left")
logo_cv = tk.Canvas(logo_fr, width=36, height=36, bg=BG_SIDEBAR, highlightthickness=0)
logo_cv.pack(side="left", padx=(0, 10))
logo_cv.create_oval(2, 2, 34, 34, fill=A_VIOLET, outline="")
logo_cv.create_text(18, 19, text="M", fill="white", font=("Georgia", 16, "bold"))
tk.Label(logo_fr, text="MAZE",  fg=T_DARK,   bg=BG_SIDEBAR, font=("Georgia", 20, "bold")).pack(side="left")
tk.Label(logo_fr, text=".AI",   fg=A_VIOLET, bg=BG_SIDEBAR, font=("Georgia", 20, "bold")).pack(side="left")

badge_fr = tk.Frame(hinner, bg="#ede9fe", padx=10, pady=4)
badge_fr.pack(side="left", padx=16, pady=4)
tk.Label(badge_fr, text="Algorithm Explorer", fg=A_VIOLET, bg="#ede9fe",
         font=("Helvetica", 9, "bold")).pack()

tk.Frame(root, bg=BORDER_CARD, height=1).pack(fill="x")

# BODY
body = tk.Frame(root, bg=BG_PAGE, padx=18, pady=14)
body.pack(fill="both", expand=True)

# ── SIDEBAR ──────────────────────────────────────────────────
sidebar = tk.Frame(body, bg=BG_PAGE, width=200)
sidebar.pack(side="left", fill="y", padx=(0, 16))
sidebar.pack_propagate(False)

# --- MODE CARD -----------------------------------------------
mode_card = card(sidebar, pady=(0, 10))
section_lbl(mode_card, "✦ Draw Mode")

mode_buttons = {}
MODE_CFG = [
    ("wall",  "⬛ Wall",  A_WARM,  "#fff3e0"),
    ("start", "◎ Start", A_MINT,  "#ecfdf5"),
    ("end",   "✕ End",   A_CORAL, "#fff1f2"),
]


def set_mode(m):
    global mode
    mode = m
    for key, (btn, col, light) in mode_buttons.items():
        if key == m:
            btn.config(bg=col,   fg="white", highlightbackground=col)
        else:
            btn.config(bg=light, fg=col,     highlightbackground=BORDER_CARD)


for key, label, col, light in MODE_CFG:
    b = tk.Button(mode_card, text=label, bg=light, fg=col,
                  activebackground=col, activeforeground="white",
                  font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                  highlightthickness=1, highlightbackground=BORDER_CARD,
                  anchor="w", padx=10)
    b.pack(fill="x", pady=2, ipady=6)
    b.config(command=lambda k=key: set_mode(k))
    mode_buttons[key] = (b, col, light)

    def _make_hover(k, bn, c, lt):
        def _in(e):  bn.config(bg=c, fg="white")
        def _out(e): bn.config(bg=(c if mode == k else lt),
                                fg=("white" if mode == k else c))
        bn.bind("<Enter>", _in)
        bn.bind("<Leave>", _out)
    _make_hover(key, b, col, light)

# --- ALGORITHM CARD ---
algo_card = card(sidebar, pady=(0, 10))
section_lbl(algo_card, "⚙ Algorithm")

sty = ttk.Style()
sty.theme_use("clam")
sty.configure("G.TCombobox",
               fieldbackground="#f5f3ff", background="#f5f3ff",
               foreground=T_DARK, bordercolor=A_VIOLET,
               lightcolor="#f5f3ff", darkcolor="#f5f3ff",
               arrowcolor=A_VIOLET, selectbackground=A_VIOLET,
               selectforeground="white")
sty.map("G.TCombobox",
        fieldbackground=[("readonly", "#f5f3ff")],
        foreground=[("readonly", T_DARK)])

algo_var  = tk.StringVar(value="A*")
algo_menu = ttk.Combobox(algo_card, textvariable=algo_var,
                          values=["A*", "BFS", "Dijkstra"],
                          state="readonly", style="G.TCombobox")
algo_menu.pack(fill="x", ipady=4, pady=(0, 2))

# --- TEMPLATE CARD ---
tmpl_card = card(sidebar, pady=(0, 10))
section_lbl(tmpl_card, "◈ Maze Template")

maze_menu = ttk.Combobox(tmpl_card,
                          values=["Empty", "Checkerboard", "Spiral",
                                  "Vertical Bars", "The Box"],
                          state="readonly", style="G.TCombobox")
maze_menu.current(0)
maze_menu.pack(fill="x", ipady=4)

# --- ACTIONS CARD ---
act_card = card(sidebar, pady=(0, 10))
section_lbl(act_card, "▶ Actions")

btn_solve = tk.Button(act_card, text="▶ SOLVE",
                       bg=A_VIOLET, fg="white",
                       activebackground=A_VIOLET_DRK, activeforeground="white",
                       font=("Helvetica", 11, "bold"),
                       relief="flat", bd=0, cursor="hand2", highlightthickness=0)
btn_solve.pack(fill="x", ipady=10, pady=(0, 4))
btn_solve.bind("<Enter>", lambda e: btn_solve.config(bg=A_VIOLET_DRK))
btn_solve.bind("<Leave>", lambda e: btn_solve.config(bg=A_VIOLET))

make_btn(act_card, "↺ Clear",        lambda: load_maze(),         fg=A_INDIGO, ipady=7)
make_btn(act_card, "? Instructions", lambda: show_instructions(), fg=T_MID,    ipady=5)

# --- LEGEND CARD ---
leg_card = card(sidebar, pady=(0, 0))
section_lbl(leg_card, "◉ Legend")

LEGEND = [
    (CELL_START,   CELL_START_DK, "Start"),
    (CELL_END,     CELL_END_DK,   "End"),
    (CELL_WALL,    CELL_WALL_DRK, "Wall"),
    (CELL_VISITED, CELL_VIS_DRK,  "Explored"),
    (CELL_PATH,    CELL_PATH_DRK, "Shortest Path"),
    (CELL_EMPTY,   "#a5b4fc",     "Empty Cell"),
]
for fill, border, label in LEGEND:
    leg_row = tk.Frame(leg_card, bg=BG_CARD, pady=2)
    leg_row.pack(fill="x")
    sw = tk.Canvas(leg_row, width=16, height=16, bg=BG_CARD, highlightthickness=0)
    sw.pack(side="left", padx=(0, 8))
    sw.create_rectangle(2, 2, 14, 14, fill=fill, outline=border, width=1.2)
    tk.Label(leg_row, text=label, fg=T_MID, bg=BG_CARD,
             font=FONT_SMALL).pack(side="left", anchor="w")

# CANVAS
right = tk.Frame(body, bg=BG_PAGE)
right.pack(side="left", fill="both", expand=True)

canvas_shell    = tk.Frame(right, bg=BORDER_CARD)
canvas_shell.pack()
canvas_inner_fr = tk.Frame(canvas_shell, bg=BG_CANVAS, padx=CANVAS_PAD, pady=CANVAS_PAD)
canvas_inner_fr.pack(padx=1, pady=1)
canvas = tk.Canvas(canvas_inner_fr, width=DRAW_W, height=DRAW_H,
                   bg=BG_CANVAS, highlightthickness=0)
canvas.pack()

# STATUS BAR
tk.Frame(root, bg=BORDER_CARD, height=1).pack(fill="x")
status_bar = tk.Frame(root, bg=BG_SIDEBAR, pady=8, padx=20)
status_bar.pack(fill="x")

status_var = tk.StringVar(value="Ready · Choose a mode and draw on the grid")
stats_var  = tk.StringVar(value="")

tk.Label(status_bar, textvariable=status_var, fg=T_MID,    bg=BG_SIDEBAR,
         font=FONT_STATUS, anchor="w").pack(side="left")
tk.Label(status_bar, textvariable=stats_var,  fg=A_VIOLET, bg=BG_SIDEBAR,
         font=("Helvetica", 9, "bold")).pack(side="right")


def set_status(msg, stats=""):
    status_var.set(msg)
    stats_var.set(stats)

# GRID CELL DRAWING
rectangles = [[None] * COLS for _ in range(ROWS)]


def cell_bbox(r, c):
    x1 = c * (CELL_SIZE + CELL_GAP) + CELL_GAP
    y1 = r * (CELL_SIZE + CELL_GAP) + CELL_GAP
    return x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE

# Initial draw
for r in range(ROWS):
    for c in range(COLS):
        x1, y1, x2, y2 = cell_bbox(r, c)
        poly = rounded_rect(canvas, x1, y1, x2, y2, CELL_RADIUS,
                             fill=CELL_EMPTY, outline="#c4c4e4", width=1.2)
        rectangles[r][c] = poly


def color_cell(r, c, fill, outline="#c4c4e4", width=1.2):
    canvas.itemconfig(rectangles[r][c], fill=fill, outline=outline, width=width)

# ANIMATION ENGINE
def animate_step(steps, idx, callback):
    if idx >= len(steps):
        callback()
        return
    r, c, fill, outline, w = steps[idx]
    color_cell(r, c, fill, outline, w)
    delay = 30 if outline == CELL_PATH_DRK else 11
    root.after(delay, animate_step, steps, idx + 1, callback)

# MOUSE HANDLING
def canvas_to_grid(ex, ey):
    col = (ex - CELL_GAP) // (CELL_SIZE + CELL_GAP)
    row = (ey - CELL_GAP) // (CELL_SIZE + CELL_GAP)
    return row, col


def handle_mouse(event, erase=False):
    row, col = canvas_to_grid(event.x, event.y)
    if not backend.in_bounds(row, col):
        return

    if erase:
        # --- erase path ---
        was_start = (row, col) == backend.start
        was_end   = (row, col) == backend.end
        backend.clear_cell(row, col)          # updates backend state
        color_cell(row, col, CELL_EMPTY, "#c4c4e4", 1.2)
        if was_start:
            set_status("Start cleared.")
        if was_end:
            set_status("End cleared.")
        return

    if mode == "wall":
        if (row, col) != backend.start and (row, col) != backend.end:
            backend.set_wall(row, col, True)
            color_cell(row, col, CELL_WALL, CELL_WALL_DRK, 1.5)

    elif mode == "start":
        old = backend.start
        if old:
            color_cell(old[0], old[1], CELL_EMPTY, "#c4c4e4", 1.2)
        backend.set_start((row, col))
        color_cell(row, col, CELL_START, CELL_START_DK, 2)
        set_status(f"Start placed at ({row}, {col})")

    elif mode == "end":
        old = backend.end
        if old:
            color_cell(old[0], old[1], CELL_EMPTY, "#c4c4e4", 1.2)
        backend.set_end((row, col))
        color_cell(row, col, CELL_END, CELL_END_DK, 2)
        set_status(f"End placed at ({row}, {col})")


canvas.bind("<Button-1>",    lambda e: handle_mouse(e))
canvas.bind("<B1-Motion>",   lambda e: handle_mouse(e))
canvas.bind("<Button-3>",    lambda e: handle_mouse(e, True))
canvas.bind("<B3-Motion>",   lambda e: handle_mouse(e, True))

# RESULTS POPUP
def show_results(algo_name, path_len, nodes_explored, path_found):
    win = tk.Toplevel(root)
    win.title("Results — MAZE.AI")
    win.configure(bg=BG_PAGE)
    win.resizable(False, False)
    win.grab_set()

    root.update_idletasks()
    rx = root.winfo_x() + root.winfo_width()  // 2
    ry = root.winfo_y() + root.winfo_height() // 2
    win.geometry(f"+{rx - 185}+{ry - 215}")

    banner_col = A_VIOLET if path_found else A_CORAL

    # Banner
    banner = tk.Frame(win, bg=banner_col, padx=28, pady=22)
    banner.pack(fill="x")
    icon_cv = tk.Canvas(banner, width=56, height=56, bg=banner_col, highlightthickness=0)
    icon_cv.pack()
    icon_cv.create_oval(3, 3, 53, 53, fill="white", outline="")
    icon_cv.create_text(28, 30,
                         text="✓" if path_found else "✗",
                         fill=banner_col, font=("Helvetica", 24, "bold"))
    tk.Label(banner,
             text="Path Found!" if path_found else "No Path Found",
             fg="white", bg=banner_col,
             font=("Georgia", 16, "bold")).pack(pady=(10, 3))
    algo_badge = tk.Frame(banner, bg="white", padx=12, pady=3)
    algo_badge.pack(pady=(0, 2))
    tk.Label(algo_badge, text=f"via {algo_name}", fg=banner_col, bg="white",
             font=("Helvetica", 9, "bold")).pack()

    # Stat cards
    stats_frame = tk.Frame(win, bg=BG_PAGE, padx=20, pady=18)
    stats_frame.pack(fill="x")

    def stat_card(parent, icon, label, value, accent):
        shell = tk.Frame(parent, bg=BORDER_CARD)
        shell.pack(side="left", expand=True, fill="both", padx=5)
        inner = tk.Frame(shell, bg=BG_CARD, padx=14, pady=16)
        inner.pack(fill="both", padx=1, pady=1)
        tk.Frame(inner, bg=accent, height=3).pack(fill="x", pady=(0, 12))
        tk.Label(inner, text=icon,       fg=accent, bg=BG_CARD,
                 font=("Helvetica", 20)).pack()
        tk.Label(inner, text=str(value), fg=T_DARK, bg=BG_CARD,
                 font=("Georgia", 22, "bold")).pack(pady=(5, 2))
        tk.Label(inner, text=label,      fg=T_MID,  bg=BG_CARD,
                 font=("Helvetica", 8)).pack()

    if path_found:
        efficiency = round((path_len / nodes_explored) * 100) if nodes_explored else 0
        stat_card(stats_frame, "↗", "Path Length",     path_len,       A_VIOLET)
        stat_card(stats_frame, "⬡", "Nodes Explored",  nodes_explored, A_INDIGO)
        stat_card(stats_frame, "◎", "Efficiency",      f"{efficiency}%", A_MINT)
    else:
        stat_card(stats_frame, "⬡", "Nodes Explored",  nodes_explored, A_INDIGO)
        stat_card(stats_frame, "✕", "Path Found",       "None",         A_CORAL)

    # Algorithm blurb
    blurbs = {
        "A*":       "A* uses a heuristic to guide the search toward the goal — optimally fast.",
        "BFS":      "BFS explores neighbours level by level — guaranteed shortest path on unweighted grids.",
        "Dijkstra": "Dijkstra expands the lowest-cost node first — optimal for all weighted graphs.",
    }
    blurb_fr = tk.Frame(win, bg=BG_PAGE, padx=25, pady=(0, 6))
    blurb_fr.pack(fill="x")
    info_bg  = "#f5f3ff"
    info_box = tk.Frame(blurb_fr, bg=info_bg, padx=16, pady=12)
    info_box.pack(fill="x")
    tk.Frame(info_box, bg=A_VIOLET, width=3).pack(side="left", fill="y", padx=(0, 10))
    tk.Label(info_box, text=blurbs.get(algo_name, ""),
             fg=A_VIOLET, bg=info_bg,
             font=("Helvetica", 8, "italic"),
             wraplength=290, justify="left").pack(side="left")

    # Close button
    btn_fr = tk.Frame(win, bg=BG_PAGE, padx=25, pady=(8, 22))
    btn_fr.pack(fill="x")
    close_btn = tk.Button(btn_fr, text="Close ✕",
                           bg=banner_col, fg="white",
                           activebackground=A_VIOLET_DRK, activeforeground="white",
                           font=("Helvetica", 10, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           highlightthickness=0, command=win.destroy)
    close_btn.pack(fill="x", ipady=11)
    close_btn.bind("<Enter>", lambda e: close_btn.config(bg=A_VIOLET_DRK))
    close_btn.bind("<Leave>", lambda e: close_btn.config(bg=banner_col))

# SOLVE
def solve():
    if not backend.start or not backend.end:
        messagebox.showwarning("MAZE.AI",
                               "Please place both a Start ◎ and End ✕ point first.")
        return

    # Clear previous visited / path colouring
    for r in range(ROWS):
        for c in range(COLS):
            fill = canvas.itemcget(rectangles[r][c], "fill")
            if fill in (CELL_VISITED, CELL_PATH):
                color_cell(r, c, CELL_EMPTY, "#c4c4e4", 1.2)

    choice = algo_var.get()
    set_status(f"Running {choice}…", "computing…")
    root.update_idletasks()

    # ── delegate to backend ─
    path, visited = backend.solve(choice)

    steps = []
    for r, c in visited:
        if (r, c) not in (backend.start, backend.end):
            steps.append((r, c, CELL_VISITED, CELL_VIS_DRK, 1.5))
    if path:
        for r, c in path:
            if (r, c) != backend.end:
                steps.append((r, c, CELL_PATH, CELL_PATH_DRK, 2.0))

    def on_done():
        if backend.start:
            color_cell(backend.start[0], backend.start[1], CELL_START, CELL_START_DK, 2)
        if backend.end:
            color_cell(backend.end[0],   backend.end[1],   CELL_END,   CELL_END_DK,   2)
        if path:
            set_status(f"✓ Path found using {choice}",
                       f"Length: {len(path)}  Explored: {len(visited)}")
            show_results(choice, len(path), len(visited), True)
        else:
            set_status("✗ No path found between start and end.", "")
            show_results(choice, 0, len(visited), False)

    animate_step(steps, 0, on_done)


btn_solve.config(command=solve)

# LOAD MAZE  (template selection + clear)
def load_maze(event=None):
    idx = maze_menu.current()

    # ── delegate to backend ──────────────────────────────────
    backend.apply_template(idx)
    # ─────────────────────────────────────────────────────────

    for r in range(ROWS):
        for c in range(COLS):
            if backend.grid[r][c]:
                color_cell(r, c, CELL_WALL, CELL_WALL_DRK, 1.5)
            else:
                color_cell(r, c, CELL_EMPTY, "#c4c4e4", 1.2)

    set_status("Grid cleared · Select a mode and click the grid to begin.", "")


maze_menu.bind("<<ComboboxSelected>>", load_maze)

# INSTRUCTIONS POPUP
def show_instructions():
    win = tk.Toplevel(root)
    win.title("How to Use — MAZE.AI")
    win.configure(bg=BG_PAGE)
    win.resizable(False, False)
    win.grab_set()

    root.update_idletasks()
    rx = root.winfo_x() + root.winfo_width()  // 2
    ry = root.winfo_y() + root.winfo_height() // 2
    win.geometry(f"+{rx - 185}+{ry - 230}")

    hdr = tk.Frame(win, bg=A_VIOLET, padx=24, pady=18)
    hdr.pack(fill="x")
    ic2 = tk.Canvas(hdr, width=40, height=40, bg=A_VIOLET, highlightthickness=0)
    ic2.pack(side="left", padx=(0, 14))
    ic2.create_oval(2, 2, 38, 38, fill="white", outline="")
    ic2.create_text(20, 21, text="?", fill=A_VIOLET, font=("Helvetica", 17, "bold"))
    tk.Label(hdr, text="How to Use MAZE.AI",
             fg="white", bg=A_VIOLET,
             font=("Georgia", 13, "bold")).pack(side="left", anchor="w")

    body_f = tk.Frame(win, bg=BG_PAGE, padx=24, pady=14)
    body_f.pack(fill="both", expand=True)

    rows_data = [
        ("Left Click / Drag",  "Draw walls on the grid"),
        ("Right Click / Drag", "Erase walls or markers"),
        ("Wall Mode",          "Paint walls by clicking or dragging"),
        ("Start Mode",         "Place the green start point (◎)"),
        ("End Mode",           "Place the red end point (✕)"),
        ("Algorithm",          "Choose A*, BFS, or Dijkstra"),
        ("Maze Template",      "Load a prebuilt maze layout"),
        ("SOLVE",              "Run the algorithm and animate"),
        ("Clear",              "Reset grid to current template"),
    ]
    for i, (k, v) in enumerate(rows_data):
        bg = "#f5f3ff" if i % 2 == 0 else BG_PAGE
        rw = tk.Frame(body_f, bg=bg, padx=12, pady=7)
        rw.pack(fill="x")
        tk.Label(rw, text=k, fg=A_VIOLET, bg=bg,
                 font=("Helvetica", 9, "bold"), width=20, anchor="w").pack(side="left")
        tk.Label(rw, text=v, fg=T_DARK,   bg=bg,
                 font=FONT_SMALL, anchor="w").pack(side="left")

    close = tk.Button(win, text="Got it ✓",
                       bg=A_VIOLET, fg="white",
                       font=("Helvetica", 10, "bold"),
                       relief="flat", bd=0, cursor="hand2",
                       highlightthickness=0, command=win.destroy)
    close.pack(fill="x", padx=24, pady=(4, 22), ipady=10)
    close.bind("<Enter>", lambda e: close.config(bg=A_VIOLET_DRK))
    close.bind("<Leave>", lambda e: close.config(bg=A_VIOLET))

set_mode("wall")
load_maze()
root.mainloop()
