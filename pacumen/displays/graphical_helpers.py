def format_color(r, g, b):
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def color_to_vector(color):
    return map(lambda x: int(x, 16) / 256.0, [color[1:3], color[3:5], color[5:7]])
