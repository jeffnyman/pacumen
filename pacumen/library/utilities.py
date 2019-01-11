import sys
import random
import inspect

from pacumen.library.counter import Counter


def manhattan_distance(xy1, xy2):
    """
    Returns the Manhattan distance between points xy1 and xy2. The Manhattan
    distance refers to the distance between two points on a grid based on a
    strictly horizontal and/or vertical path, as opposed to the diagonal
    distance.

    :param xy1: first point
    :param xy2: second point
    :return: manhattan distance between first and second point
    """
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


def nearest_point(position):
    """
    Finds the nearest grid point to a position.

    :param position: the position to find the nearest point to
    :return: the nearest point to the passed in position
    """
    (current_row, current_col) = position

    grid_row = int(current_row + 0.5)
    grid_col = int(current_col + 0.5)

    return grid_row, grid_col


def choose_from_distribution(distribution):
    if type(distribution) == dict or type(distribution) == Counter:
        return sample(distribution)


def sample(distribution, values=None):
    """
    Returns a specific value that is a sample from a passed in distribution
    of values. An example here is that a distribution might be passed in
    like this:

    {'North': 0.5, 'South': 0.5}

    So the individual items of this distribution are represented as a list
    of tuples:

    [('North', 0.5), ('South', 0.5)]

    The distributions are then:

    [0.5, 0.5]

    And the distribution values are:

    ['North', 'South']
    """
    if type(distribution) == Counter:
        items = sorted(distribution.items())
        distribution = [i[1] for i in items]
        values = [i[0] for i in items]

    if sum(distribution) != 1:
        distribution = normalize(distribution)

    choice = random.random()

    i, total = 0, distribution[0]

    """
    The loop can seem a little odd. Consider you have this distribution:
    
    {'North': 0.25, 'South': 0.25, 'East': 0.25, 'West': 0.25}

    Which breaks down to this: [0.25, 0.25, 0.25, 0.25]

    To the total (before loop) would be: 0.25.
    
    Let's say the random choice was: 0.9131881194285504.
    
    So the while loop will iterate three times as such:
    
    : i = 1, total = distribution[1] + distribution[0] = 0.25 + 0.25 = 0.5
    : i = 2, total = distribution[2] + distribution = 0.25 + 0.5 = 0.75
    : i = 3, total = distribution[3] + distribution = 0.25 + 0.75 = 1

    so the total (after the loop): 1.0 and i is 3. This means values[3]
    will be returned, which means "West" from the distribution.
    """

    while choice > total:
        i += 1
        total += distribution[i]

    return values[i]


def normalize(vector_or_counter):
    """
    Normalizes a vector or counter by dividing each value by the sum of
    all of the values.
    """
    normalized_counter = Counter()

    if type(vector_or_counter) == type(normalized_counter):
        counter = vector_or_counter
        total = float(counter.total_count())

        if total == 0:
            return counter

        for key in list(counter.keys()):
            value = counter[key]
            normalized_counter[key] = value / total

        return normalized_counter
    else:
        vector = vector_or_counter
        s = float(sum(vector))

        if s == 0:
            return vector

        return [el / s for el in vector]


def lookup(name, namespace):
    """
    Gets a method or class from any imported module from its name.
    """
    dots = name.count('.')

    if dots > 0:
        module_name, object_name = '.'.join(name.split('.')[:-1]), name.split('.')[-1]
        the_module = __import__(module_name)

        return getattr(the_module, object_name)
    else:
        modules = [obj for obj in list(namespace.values()) if str(type(obj)) == "<type 'module'>"]
        options = [getattr(the_module, name) for the_module in modules if name in dir(the_module)]
        options += [obj[1] for obj in list(namespace.items()) if obj[0] == name]

        if len(options) == 1:
            return options[0]

        if len(options) > 1:
            raise Exception('Name conflict for %s')

        raise Exception('%s not found as a method or class' % name)


def raise_not_defined():
    file_name = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" % (method, line, file_name))

    sys.exit(1)


def abstract():
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')


def file_logger():
    import os
    import logging
    import contextlib

    with contextlib.suppress(FileNotFoundError):
        os.remove('output.log')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.getLevelName(logging.INFO))

    handler = logging.FileHandler('output.log')

    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
