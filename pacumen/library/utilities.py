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
