import os

from pacumen.mechanics.grid import Grid


class Layout:
    def process_layout_text(self, layout_text):
        """
        The width (x) is how many elements are in a single cell. The
        height (y) is how many cells there are. So this bit of logic
        counts down the rows and, for each row, gets each element of
        that row.
        """
        maximum_y = self.height - 1

        for y in range(self.height):
            for x in range(self.width):
                layout_char = layout_text[maximum_y - y][x]
                self.process_layout_characters(x, y, layout_char)

    def process_layout_characters(self, x, y, character):
        if character == "%":
            self.walls[x][y] = True
        elif character == ".":
            self.dots[x][y] = True

    def is_wall(self, position):
        row, column = position
        return self.walls[row][column]

    def __init__(self, layout_text):
        self.layout_text = layout_text
        self.width = len(layout_text[0])
        self.height = len(layout_text)
        self.walls = Grid(self.width, self.height, False)
        self.dots = Grid(self.width, self.height, False)
        self.process_layout_text(layout_text)
        self.total_dots = len(self.dots.as_list())

    def __str__(self):
        return "\n".join(self.layout_text)


def load_layout(fullname):
    if not os.path.exists(fullname):
        return None

    layout_file = open(fullname)

    try:
        return Layout([line.strip() for line in layout_file])
    finally:
        layout_file.close()


def get_layout(name, back_path=1):
    """
    This method checks for name.lay in the layouts directory. If the file
    is not found there, it checks for name.lay in the project root. The
    method will append the ".lay" extension for you if it's not provided.
    Finally, the method will also check one level above the project root.
    This can be configured by changing the value of `back_path`.
    """
    if name.endswith(".lay"):
        layout = load_layout("layouts/" + name)

        if layout is None:
            layout = load_layout(name)
    else:
        layout = load_layout("layouts/" + name + ".lay")

        if layout is None:
            layout = load_layout(name + ".lay")

    if layout is None and back_path > 0:
        current_directory = os.path.abspath(".")
        os.chdir("..")
        layout = get_layout(name, back_path - 1)
        os.chdir(current_directory)

    return layout


def test():
    game_layout = get_layout("testing")
    print("Layout as read from file:")
    print(game_layout)
    print("----------------")
    print("Width:", game_layout.width)
    print("Height:", game_layout.height)
    print("----------------")
    print("Walls and Dots are Grids")
    print("----------------")
    print("Walls:\n{}".format(game_layout.walls))
    print("Is 0,0 a wall? (True) -", game_layout.is_wall((0, 0)))
    print("Is 1,1 a wall? (False) -", game_layout.is_wall((1, 1)))
    print("Hash of walls:", hash(game_layout.walls))
    print("----------------")
    print("Dots:\n{}".format(game_layout.dots))
    print("Hash of dots:", hash(game_layout.dots))
    print("Total Dots:", game_layout.total_dots)
    print("Dot Locations:", game_layout.dots.as_list())
    print("----------------")
