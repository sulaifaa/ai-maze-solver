import heapq
from collections import deque

# GRID CONSTANTS
ROWS, COLS = 20, 20

# GRID STATE 

grid  = [[0] * COLS for _ in range(ROWS)]   # 0 = open, 1 = wall
start = None   # (row, col) tuple or None
end   = None   # (row, col) tuple or None

# GRID HELPERS
def reset_grid():
    """Clear grid, start and end back to defaults."""
    global grid, start, end
    grid  = [[0] * COLS for _ in range(ROWS)]
    start = None
    end   = None


def set_start(pos):
    """Set the start position (row, col)."""
    global start
    start = pos
    if pos is not None:
        grid[pos[0]][pos[1]] = 0   # start cell is never a wall


def set_end(pos):
    """Set the end position (row, col)."""
    global end
    end = pos
    if pos is not None:
        grid[pos[0]][pos[1]] = 0   # end cell is never a wall


def set_wall(row, col, is_wall=True):
    """Mark or clear a wall at (row, col). Refuses to overwrite start/end."""
    if (row, col) == start or (row, col) == end:
        return
    grid[row][col] = 1 if is_wall else 0


def clear_cell(row, col):
    """Remove wall at (row, col), also clears start/end if they were there."""
    global start, end
    grid[row][col] = 0
    if (row, col) == start:
        start = None
    if (row, col) == end:
        end = None



def in_bounds(row, col):
    return 0 <= row < ROWS and 0 <= col < COLS


# MAZE TEMPLATES
def template_empty():
    """All open cells."""
    return [[0] * COLS for _ in range(ROWS)]


def template_checkerboard():
    """Sparse checkerboard of walls."""
    return [[1 if (i + j) % 4 == 0 else 0 for j in range(COLS)] for i in range(ROWS)]


def template_spiral():
    """Simple rectangular spiral border with one opening."""
    g = [[0] * COLS for _ in range(ROWS)]
    for i in range(4, 16):
        g[4][i]  = 1
        g[16][i] = 1
        g[i][4]  = 1
        if i < 15:
            g[i][16] = 1
    return g


def template_vertical_bars():
    """Vertical wall bars with gaps."""
    return [[1 if j % 4 == 0 and i % 5 != 0 else 0 for j in range(COLS)] for i in range(ROWS)]


def template_the_box():
    """Walled border with one entrance on the left mid-side."""
    g = [[0] * COLS for _ in range(ROWS)]
    for i in range(ROWS):
        for j in range(COLS):
            if i == 0 or i == ROWS - 1 or j == 0 or j == COLS - 1:
                if not (i == ROWS // 2 and j == 0):   # leave one gap
                    g[i][j] = 1
    return g


# Map index → builder (matches the Combobox order in the GUI)
TEMPLATE_BUILDERS = [
    template_empty,         # 0 – Empty
    template_checkerboard,  # 1 – Checkerboard
    template_spiral,        # 2 – Spiral
    template_vertical_bars, # 3 – Vertical Bars
    template_the_box,       # 4 – The Box
]


def apply_template(index):
    """
    Replace the global grid with the template at *index*.
    Resets start and end as well.
    Returns the new grid (same object as the global).
    """
    global grid, start, end
    builder = TEMPLATE_BUILDERS[index] if 0 <= index < len(TEMPLATE_BUILDERS) else template_empty
    grid    = builder()
    start   = None
    end     = None
    return grid


# PATHFINDING HELPERS
def get_neighbors(pos):
    """Return all open, in-bounds 4-directional neighbours of *pos*."""
    r, c = pos
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and grid[nr][nc] == 0:
            result.append((nr, nc))
    return result


def reconstruct_path(came_from, current):
    """Walk the came_from dict back to the start and return the path."""
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    return path[::-1]

# ALGORITHMS
def run_astar(s, e):
    """A* with Manhattan-distance heuristic and deterministic tie-breaking."""
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set  = []
    counter   = 0
    heapq.heappush(open_set, (0, counter, s))

    came_from = {}
    g_score   = {(r, c): float('inf') for r in range(ROWS) for c in range(COLS)}
    g_score[s] = 0
    visited_set = set()
    visited = []

    while open_set:
        _, _, curr = heapq.heappop(open_set)
        if curr in visited_set:
            continue
        visited_set.add(curr)
        visited.append(curr)

        if curr == e:
            return reconstruct_path(came_from, e), visited

        for n in get_neighbors(curr):
            tg = g_score[curr] + 1
            if tg < g_score[n]:
                came_from[n] = curr
                g_score[n]   = tg
                counter += 1
                heapq.heappush(open_set, (tg + h(n, e), counter, n))

    return None, visited


def run_dijkstra(s, e):
    """Dijkstra's algorithm with deterministic tie-breaking."""
    open_set  = []
    counter   = 0
    heapq.heappush(open_set, (0, counter, s))

    came_from = {}
    dist      = {(r, c): float('inf') for r in range(ROWS) for c in range(COLS)}
    dist[s]   = 0
    visited_set = set()
    visited = []

    while open_set:
        d, _, curr = heapq.heappop(open_set)
        if curr in visited_set:
            continue
        visited_set.add(curr)
        visited.append(curr)

        if curr == e:
            return reconstruct_path(came_from, e), visited
        for n in get_neighbors(curr):
            new_dist = dist[curr] + 1
            if new_dist < dist[n]:
                dist[n] = new_dist
                came_from[n] = curr
                counter += 1
                heapq.heappush(open_set, (new_dist, counter, n))

    return None, visited


def run_bfs(s, e):
    """Breadth-First Search — deterministic."""
    queue = deque([s])
    came_from = {s: None}
    visited_set = set([s])
    visited = []

    while queue:
        curr = queue.popleft()
        visited.append(curr)

        if curr == e:
            return reconstruct_path(came_from, e), visited

        for n in get_neighbors(curr):
            if n not in visited_set:
                visited_set.add(n)
                came_from[n] = curr
                queue.append(n)

    return None, visited

# Convenience dispatch used by the GUI
ALGORITHM_MAP = {
    "A*":       run_astar,
    "BFS":      run_bfs,
    "Dijkstra": run_dijkstra,
}


def solve(algorithm_name):

    if start is None or end is None:
        raise ValueError("Both start and end must be set before solving.")
    runner = ALGORITHM_MAP.get(algorithm_name)
    if runner is None:
        raise ValueError(f"Unknown algorithm: {algorithm_name!r}")
    return runner(start, end)
