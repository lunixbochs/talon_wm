from dataclasses import dataclass

from talon import Module, ui
from talon.types import Rect, Point2d

@dataclass
class GridSpec:
    cols: int
    rows: int

    def for_screen(self, screen: ui.Screen) -> 'Grid':
        rect = screen.visible_rect
        colsize = int(rect.width  // self.cols)
        rowsize = int(rect.height // self.rows)
        cols = [rect.x + x for x in range(0, int(rect.width),  colsize)] + [rect.right]
        rows = [rect.y + y for y in range(0, int(rect.height), rowsize)] + [rect.bot]
        return Grid(rect, cols, rows, colsize, rowsize)

@dataclass
class Grid:
    rect: Rect
    cols: list[int]
    rows: list[int]
    colsize: int
    rowsize: int

    def nearest(self, p: Point2d, extents: bool=False) -> tuple[tuple[int, int], Point2d]:
        cols = self.cols if extents else self.cols[:-1]
        rows = self.rows if extents else self.rows[:-1]
        cols = sorted(enumerate(cols), key=lambda x: abs(p.x - x[1]))
        rows = sorted(enumerate(rows), key=lambda x: abs(p.y - x[1]))
        (col_idx, col), (row_idx, row) = cols[0], rows[0]
        return (col_idx, row_idx), Point2d(col, row)

    def snap_point(self, p: Point2d, extents: bool=False) -> Point2d:
        idx, pos = self.nearest(p, extents=extents)
        return pos

    def snap_rect(self, rect: Rect) -> Rect:
        _, pos       = self.nearest(rect.pos)
        _, bot_right = self.nearest(Point2d(rect.right, rect.bot), extents=True)
        size = bot_right - pos
        snapped = Rect(*pos, *size)
        return snapped

    def is_rect_on_grid(self, rect: Rect, slip=5.0) -> bool:
        ref = self.snap_rect(rect)
        deviance = min(
            abs(rect.x - ref.x),
            abs(rect.y - ref.y),
            abs(rect.width - ref.width),
            abs(rect.height - ref.height),
        )
        return deviance <= slip

# (x, y)
shift_directions = {
    'left':  (-1,  0),
    'right': ( 1,  0),
    'up':    ( 0, -1),
    'down':  ( 0,  1),
}

# Rect(x, y, width, height) indicates screen % to snap each value
splits = {
    'top':    Rect(0.0, 0.0, 1.0, 0.5),
    'right':  Rect(0.5, 0.0, 0.5, 1.0),
    'bottom': Rect(0.0, 0.5, 1.0, 0.5),
    'left':   Rect(0.0, 0.0, 0.5, 1.0),

    'top-right':    Rect(0.5, 0.0, 0.5, 0.5),
    'bottom-right': Rect(0.5, 0.5, 0.5, 0.5),
    'bottom-left':  Rect(0.0, 0.5, 0.5, 0.5),
    'top-left':     Rect(0.0, 0.0, 0.5, 0.5),
}

grid_spec = GridSpec(8, 6)

grid_margin = 4

def rect_div(rect1: Rect, rect2: Rect) -> Rect:
    "Divide rect1 (small) into a percentage of rect2 (large)"
    pos = (rect1.pos - rect2.pos) / rect2.size
    size = rect1.size / rect2.size
    return Rect(*pos, *size)

def rect_mul(rect1: Rect, rect2: Rect) -> Rect:
    "Multiply rect1 (% rect) into rect2 (large) space"
    pos  = rect2.pos + (rect1.pos * rect2.size)
    size = rect1.size * rect2.size
    return Rect(*pos, *size)

def win_cycle_screen(win: ui.Window, offset: int) -> None:
    old_screen = win.screen
    screens = ui.screens()
    new_screen = screens[(screens.index(old_screen) + offset) % len(screens)]
    # TODO: more window resize logic
    prect = rect_div(win.rect, old_screen.visible_rect)
    win.rect = rect_mul(prect, new_screen.visible_rect)

def pad_rect(rect: Rect) -> Rect:
    return Rect(rect.x + (grid_margin / 2), rect.y + (grid_margin / 2), rect.width - grid_margin, rect.height - grid_margin);

# TODO something less naive here

win_last_rect = {}
def toggle_window_rect(win: ui.Window, rect: Rect, fuzz=4) -> None:
    deviance = max(
        abs(rect.x - win.rect.x),
        abs(rect.y - win.rect.y),
        abs(rect.width - win.rect.width),
        abs(rect.height - win.rect.height),
    )
    if (deviance <= fuzz):
        if win_last_rect[win] != None:
            win.rect = win_last_rect[win]
            del win_last_rect[win]
        else:
            pos = rect.pos + win.screen.visible_rect.center - rect.center
            rect.x, rect.y = pos
            win.rect = rect
    else:
        win_last_rect[win] = win.rect
        win.rect = rect

mod = Module()
@mod.action_class
class Actions:
    def snap_split(name: str):
        "snap to a screen split"
        win = ui.active_window()
        split_rect  = splits[name]
        screen_rect = win.screen.visible_rect
        rect = rect_mul(split_rect, screen_rect)
        win.rect = pad_rect(rect)

    def snap_shift(direction: str):
        "shift on grid"
        xd, yd = shift_directions[direction]
        win = ui.active_window()
        grid = grid_spec.for_screen(win.screen)
        rect = grid.snap_rect(win.rect)
        rect.x += grid.colsize * xd
        rect.y += grid.rowsize * yd
        rect = grid.snap_rect(rect)
        win.rect = pad_rect(rect)

    def snap_grow(direction: str):
        "grow on grid"
        win = ui.active_window()
        xd, yd = shift_directions[direction]
        win = ui.active_window()
        grid = grid_spec.for_screen(win.screen)
        rect = grid.snap_rect(win.rect)
        rect.x += grid.colsize * xd if xd < 0 else 0
        rect.y += grid.rowsize * yd if yd < 0 else 0
        rect.width  += grid.colsize * abs(xd)
        rect.height += grid.rowsize * abs(yd)
        rect = grid.snap_rect(rect)
        win.rect = pad_rect(rect)

    def snap_shrink(direction: str):
        "shrink on grid"
        win = ui.active_window()
        xd, yd = shift_directions[direction]
        win = ui.active_window()
        grid = grid_spec.for_screen(win.screen)
        rect = grid.snap_rect(win.rect)
        if xd < 0: rect.width  += grid.colsize * xd
        else:      rect.x      += grid.colsize * xd
        if yd < 0: rect.height += grid.colsize * yd
        else:      rect.y      += grid.colsize * yd
        rect = grid.snap_rect(rect)
        win.rect = pad_rect(rect)

    def snap_toggle_fullscreen():
        "toggle fullscreen"
        win = ui.active_window()
        win.element.AXFullScreen = not win.element.AXFullScreen

    def snap_toggle_maximize():
        "padded maximize"
        win = ui.active_window()
        toggle_window_rect(win, pad_rect(win.screen.visible_rect))

    def snap_toggle_center():
        "toggle center"
        win = ui.active_window()
        rect = win.rect
        pos = rect.pos + win.screen.visible_rect.center - rect.center
        rect.x, rect.y = pos
        toggle_window_rect(win, rect)

    def snap_next_screen():
        "move to next screen"
        win = ui.active_window()
        win_cycle_screen(win, 1)

    def snap_prev_screen():
        "move to prev screen"
        win = ui.active_window()
        win_cycle_screen(win, -1)

    def snap_grid():
        "snap to nearest grid position"
        win = ui.active_window()
        grid = grid_spec.for_screen(win.screen)
        win.rect = pad_rect(grid.snap_rect(win.rect))

    def snap_all():
        "snap all windows to nearest grid position"
        windows = [win for win in ui.windows(hidden=False) if (not win.app.background and win.id != 0 and win.title != "")]
        for win in windows:
            try:
                grid = grid_spec.for_screen(win.screen)
                win.rect = pad_rect(grid.snap_rect(win.rect))
            except Exception:
                pass # yolo
