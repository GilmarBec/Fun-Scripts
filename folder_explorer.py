import os
from typing import Self, Any, Callable
import curses


ESCAPE      = 27
PAGE_UP     = 339
PAGE_DOWN   = 338


class DirItem:
    name: str
    path: str
    is_dir: bool
    depth: int
    parent: Self

    def __init__(self, name: str, path: str, depth: int = 0, parent: Self = None):
        self.name = name
        self.path = path
        self.is_dir = os.path.isdir(path)
        self.depth = depth
        self.parent = parent


def is_ignored(filename: str) -> bool:
    # @TODO sync with .gitignore
    block_list = [".git", "__pycache__", ".idea", ".mypy_cache"]

    return filename in block_list


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdscr.refresh()
    stdscr.nodelay(False)
    key = -1

    current_list = [DirItem(name=x, path=x) for x in os.listdir() if not is_ignored(x)]
    current_list.sort(reverse=True, key=lambda x: int(x.is_dir))

    current_index = 0
    render(stdscr, current_list, current_index)

    while key != ord('q') and key != ESCAPE:  # Exit on 'q'
        key = stdscr.getch()
        stdscr.clear()

        if key == curses.KEY_UP:
            current_index -= 1
            if current_index <= 0: current_index = 0
        elif key == curses.KEY_DOWN:
            current_index += 1
            if current_index >= len(current_list): current_index = len(current_list) - 1
        elif key == curses.KEY_RIGHT:
            tmp_item = current_list[current_index]
            if tmp_item.is_dir:
                child_dir_items = [DirItem(name=x, path=os.path.join(tmp_item.path, x), depth=tmp_item.depth+1, parent=tmp_item) for x in os.listdir(tmp_item.path) if not is_ignored(x)]
                child_dir_items.sort(reverse=True, key=lambda x: int(x.is_dir))
                current_list = current_list[:current_index+1] + child_dir_items + current_list[current_index + 1:]
                current_index += 1
        elif key == curses.KEY_LEFT:
            tmp_item = current_list[current_index]
            if tmp_item.depth > 0:
                parent_index = reduce(lambda curr, prev, i: i if curr.path == tmp_item.parent.path else prev, current_list)
                last_child_index = reduce(lambda curr, prev, i: i if curr.parent and curr.parent.path == tmp_item.parent.path else prev, current_list)
                current_index = parent_index

                current_list = current_list[:current_index+1] + current_list[last_child_index + 1:]
        elif key == PAGE_UP:
            tmp_item = current_list[current_index]
            current_index = reduce(lambda curr, prev, i: i if prev is None and curr.depth == tmp_item.depth else prev, current_list)
        elif key == PAGE_DOWN:
            tmp_item = current_list[current_index]
            current_index = reduce(lambda curr, prev, i: i if curr.depth == tmp_item.depth else prev, current_list)
        elif key != -1:
            #stdscr.addstr(f"Key nº: {key}\n")
            pass

        render(stdscr, current_list, current_index)
        stdscr.refresh()

def render(stdscr, current_list, current_index):
    if current_index is None: current_index = 0
    # @TODO replace home directory by "~/" to minify folder description (regex or os function)
    stdscr.addstr(f"{os.getcwd()}\n\n")

    height, width = stdscr.getmaxyx()
    height -= 3
    start = 0
    end = len(current_list)
    if len(current_list) > height:
        start = current_index
        if len(current_list) > (height + current_index):
            end = height + current_index

    for curr in current_list[start:end]:
        # @TODO add more ascii caracters for intermediary cases
        # @TODO add possibility to pass param to see file/folder size
        msg = f"{'  ' * curr.depth + '└──'*int(bool(curr.depth))}{' > ' if current_list[current_index].path == curr.path else ' '}{curr.name}\n"
        stdscr.addstr(msg, curses.color_pair(3 if curr.is_dir else 2))

def reduce(func: Callable[[Any, Any, int], Any], iterable: list) -> Any:
    acc = None
    i = 0
    for item in iterable:
        acc = func(item, acc, i)
        i += 1

    return acc

curses.wrapper(main)
