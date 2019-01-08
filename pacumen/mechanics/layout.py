import os


class Layout:
    def __init__(self, layout_text):
        self.layout_text = layout_text


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
