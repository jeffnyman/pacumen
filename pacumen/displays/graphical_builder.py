import os
import sys
import time
import tkinter

from _tkinter import TclError
from _tkinter import DONT_WAIT

from pacumen.displays.graphical_helpers import format_color


# The root window for graphics output.
_root_window = None

# The canvas which holds graphics.
_canvas = None

# Size of canvas object.
_canvas_xs = None
_canvas_ys = None

# Current position on canvas.
_canvas_x = None
_canvas_y = None

# Background color of canvas.
_bg_color = None

# Data structures for keyboard actions.
_keys_down = {}
_keys_waiting = {}

# Holds an unprocessed key release. Key releases are delayed by up to one
# call to a keys_pressed() method in order to handle alternating keypress
# keyrelease events.
_got_release = None


def create_graphic_display(width=640, height=480, color=format_color(0, 0, 0), title=None):
    global _root_window, _canvas, _canvas_xs, _canvas_ys, _canvas_x, _canvas_y, _bg_color

    # Make sure a duplicate window is not being created.
    if _root_window is not None:
        _root_window.destroy()

    # Set up the canvas size parameters.
    _canvas_xs, _canvas_ys = width - 1, height - 1
    _canvas_x, _canvas_y = 0, _canvas_ys
    _bg_color = color

    # Create the root window.
    _root_window = tkinter.Tk()
    _root_window.protocol('WM_DELETE_WINDOW', _destroy_window)
    _root_window.title(title or "Pacumen Graphical Display")
    _root_window.resizable(0, 0)
    _root_window.configure(background="black")

    if sys.platform == "win32":
        pacumen_icon = os.path.dirname(os.path.realpath(__file__)) + "/pacman.ico"
        _root_window.iconbitmap(pacumen_icon)

    # Create the canvas object.
    try:
        _canvas = tkinter.Canvas(_root_window, width=width, height=height, highlightthickness=0)
        _canvas.pack()
        draw_background()

        # TODO: Just do a refresh here? To update idletasks.
        _canvas.update()
    except (TclError, RuntimeError):
        _root_window = None
        raise

    # Bind to key-down and key-up events.
    _root_window.bind("<KeyPress>", _key_press)
    _root_window.bind("<KeyRelease>", _key_release)
    _clear_keys()


def stop_graphic_display():
    global _root_window, _canvas

    try:
        try:
            update_display(1)

            if _root_window is not None:
                _root_window.destroy()
        except SystemExit as e:
            print('Stopping the graphical display raised an exception:', e)
    finally:
        _root_window = None
        _canvas = None
        _clear_keys()


def update_display(seconds):
    """
    The after method registers an alarm callback that is called after the
    provided number of milliseconds. Here the milliseconds are converted
    to seconds.
    """
    global _root_window

    if _root_window is None:
        time.sleep(seconds)
    else:
        _root_window.update_idletasks()
        _root_window.after(int(1000 * seconds), _root_window.quit)
        _root_window.mainloop()


def clear_display():
    global _canvas_x, _canvas_y

    _canvas.delete('all')
    draw_background()
    _canvas_x, _canvas_y = 0, _canvas_ys


def remove_from_display(x, d_o_e=None, d_w=DONT_WAIT):
    if d_o_e is None:
        d_o_e = _root_window.dooneevent

    _canvas.delete(x)

    d_o_e(d_w)


def refresh_display():
    """
    Any call to update_idletasks calls all pending idle tasks without
    processing any other events. This means no callbacks are called.
    """
    _canvas.update_idletasks()


def save_display(filename):
    ps_file = open(filename, 'w')
    ps_file.write(_canvas.postscript(pageanchor='sw', y='0.c', x='0.c'))
    ps_file.close()


def keys_pressed(d_o_e=None, d_w=DONT_WAIT):
    if d_o_e is None:
        d_o_e = _root_window.dooneevent

    if _got_release:
        d_o_e(d_w)

    return list(_keys_down.keys())


def keys_waiting():
    global _keys_waiting

    keys = list(_keys_waiting.keys())

    _keys_waiting = {}

    return keys


def wait_for_keys():
    keys = []

    while not keys:
        keys = keys_pressed()
        update_display(0.05)

    return keys


def draw_background():
    corners = [(0, 0), (0, _canvas_ys), (_canvas_xs, _canvas_ys), (_canvas_xs, 0)]
    polygon(corners, outline_color=_bg_color, fill_color=_bg_color, filled=True, smoothed=False)


def polygon(vertices, outline_color, fill_color=None, filled=1, smoothed=1, behind=0, width=1):
    # The transition from vertices to corners is more for clarity than any
    # necessity. When vertices come in, they'll look like this:
    #   [(0, 0), (0, 480), (640, 480), (640, 0)]
    # Corners will look like this:
    #   [0, 0, 0, 480, 640, 480, 640, 0]
    corners = []

    for vertex in vertices:
        corners.append(vertex[0])
        corners.append(vertex[1])

    # If the fill color is set to None, then the outline color will be used
    # for the fill.
    if fill_color is None:
        fill_color = outline_color

    # If filled is set to False, then the fill color will be transparent.
    if filled == 0:
        fill_color = ""

    poly_shape = _canvas.create_polygon(corners, outline=outline_color, fill=fill_color, smooth=smoothed, width=width)

    # If behind has a positive, non-zero value the object will be drawn
    # behind the canvas. This effectively removes the object form view
    # but not from the root_window itself.
    if behind > 0:
        _canvas.tag_lower(poly_shape, behind)

    return poly_shape


def circle(position, radius, outline_color, fill_color, endpoints=None, style='pieslice', width=2):
    x, y = position
    x0, x1 = x - radius - 1, x + radius
    y0, y1 = y - radius - 1, y + radius

    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)

    # The extent refers to the width of an arc slice in degrees. The slice
    # starts at the angle given by the `start` option and then will extend
    # counterclockwise for `extent` degrees.

    while e[0] > e[1]:
        e[1] = e[1] + 360

    return _canvas.create_arc(x0, y0, x1, y1, outline=outline_color, fill=fill_color,
                              extent=e[1] - e[0], start=e[0], style=style, width=width)


def square(position, radius, color, filled=1, behind=0):
    x, y = position

    coordinates = [(x - radius, y - radius), (x + radius, y - radius),
                   (x + radius, y + radius), (x - radius, y + radius)]

    return polygon(coordinates, color, color, filled, 0, behind=behind)


def line(here, there, color=format_color(0, 0, 0), width=2):
    x0, y0 = here[0], here[1]
    x1, y1 = there[0], there[1]

    return _canvas.create_line(x0, y0, x1, y1, fill=color, width=width)


def text(position, color, contents, font='Helvetica', size=12, style='normal', anchor="nw"):
    x, y = position
    font = (font, str(size), style)

    return _canvas.create_text(x, y, fill=color, text=contents, font=font, anchor=anchor)


def change_text(identity, new_text, font=None, size=12, style='normal'):
    _canvas.itemconfigure(identity, text=new_text)
    if font is not None:
        _canvas.itemconfigure(identity, font=(font, '-%d' % size, style))


def change_color(identity, new_color):
    _canvas.itemconfigure(identity, fill=new_color)


def move_circle(identifier, position, radius, endpoints=None):
    global _canvas_x, _canvas_y

    x, y = position
    x0, x1 = x - radius - 1, x + radius
    y0, y1 = y - radius - 1, y + radius

    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)

    while e[0] > e[1]:
        e[1] = e[1] + 360

    edit(identifier, ('start', e[0]), ('extent', e[1] - e[0]))

    move_to(identifier, x0, y0)


def move_to(element, x, y=None, d_o_e=None, d_w=DONT_WAIT):
    if d_o_e is None:
        d_o_e = _root_window.dooneevent

    if y is None:
        try:
            x, y = x
        except ValueError:
            raise Exception("Received invalid coordinates for moving element to.")

    horizontal = True
    new_coordinates = []

    current_x, current_y = _canvas.coords(element)[0:2]

    for coordinate in _canvas.coords(element):
        if horizontal:
            increment = x - current_x
        else:
            increment = y - current_y

        horizontal = not horizontal

        new_coordinates.append(coordinate + increment)

    _canvas.coords(element, *new_coordinates)

    d_o_e(d_w)


def move_by(element, x, y=None, d_o_e=None, d_w=DONT_WAIT, lift=False):
    if d_o_e is None:
        d_o_e = _root_window.dooneevent

    if y is None:
        try:
            x, y = x
        except ValueError:
            raise Exception("Received invalid coordinates for moving element by.")

    horizontal = True
    new_coordinates = []

    for coordinate in _canvas.coords(element):
        if horizontal:
            increment = x
        else:
            increment = y

        horizontal = not horizontal

        new_coordinates.append(coordinate + increment)

    _canvas.coords(element, *new_coordinates)

    d_o_e(d_w)

    if lift:
        _canvas.tag_raise(element)


def edit(identifier, *args):
    _canvas.itemconfigure(identifier, **dict(args))


def _destroy_window():
    sys.exit(0)


def _key_press(event):
    global _got_release

    _keys_down[event.keysym] = 1
    _keys_waiting[event.keysym] = 1

    _got_release = None


def _key_release(event):
    global _got_release

    try:
        del _keys_down[event.keysym]
    except KeyError:
        pass

    _got_release = 1


def _clear_keys(_event=None):
    global _keys_down, _keys_waiting, _got_release

    _keys_down = {}
    _keys_waiting = {}
    _got_release = None


def show_display():
    global _root_window

    _root_window.update_idletasks()
    _root_window.mainloop()


def test():
    create_graphic_display()
    clear_display()

    line((150, 50), (200, 200), format_color(.1, .75, .7), width=5)

    square((100, 150), 0.5 * 30, color=format_color(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0))
    square((150, 200), 0.5 * 30, color=format_color(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0), filled=False)
    square((170, 210), 0.5 * 30, color=format_color(0.0 / 100.0, 91.0 / 100.0, 100.0 / 100.0), behind=1)

    circle((150, 150), 20, format_color(0.7, 0.3, 0.0), format_color(1.0, 0.6, 0.0), endpoints=[15, -15])
    circle((350, 350), 20, format_color(0.3, 0.7, 0.0), format_color(0.6, 1.0, 0.0), style='chord', width=5)

    text((300, 300), format_color(.4, 0.13, 0.91), "SCORE: 0", "Times", 24, "bold", "center")

    ghost_shape = [
        (0, 0.3),
        (0.25, 0.75),
        (0.5, 0.3),
        (0.75, 0.75),
        (0.75, -0.5),
        (0.5, -0.75),
        (-0.5, -0.75),
        (-0.75, -0.5),
        (-0.75, 0.75),
        (-0.5, 0.3),
        (-0.25, 0.75)
    ]

    ghost_shape = [(x * 30 + 20, y * 30 + 20) for x, y in ghost_shape]
    ghost = polygon(ghost_shape, outline_color=format_color(0, .9, 0))
    move_to(ghost, (100, 100))
    polygon(ghost_shape, outline_color=format_color(.9, 0, 0), fill_color=format_color(.7, 0, 0), width=5)

    save_display("display.ps")
    show_display()
