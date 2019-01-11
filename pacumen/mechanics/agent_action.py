from pacumen.mechanics.agent_direction import Direction


class Actions:
    TOLERANCE = .001

    directions = {
        Direction.NORTH: (0, 1),
        Direction.SOUTH: (0, -1),
        Direction.EAST:  (1, 0),
        Direction.WEST:  (-1, 0),
        Direction.STOP:  (0, 0)
    }

    directions_as_list = list(directions.items())

    @staticmethod
    def get_possible_actions(config, walls):
        possible = []
        x, y = config.position
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight.
        if abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE:
            return [config.get_direction()]

        for direction, vector in Actions.directions_as_list:
            # If the position was currently (8, 1), this would find
            # all positions using the directions vector that could
            # be reached. So this would produce (8, 2), (8, 0),
            # (9, 1), (7, 1), and (8, 1). Of those directions that
            # are produced, it's then checked if any of them are
            # a wall.

            dx, dy = vector
            next_y = y_int + dy
            next_x = x_int + dx

            if not walls[next_x][next_y]:
                possible.append(direction)

        return possible

    @staticmethod
    def get_legal_neighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []

        for direction, vector in Actions.directions_as_list:
            dx, dy = vector
            next_x = x_int + dx

            if next_x < 0 or next_x == walls.width:
                continue

            next_y = y_int + dy

            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))

        return neighbors

    @staticmethod
    def get_successor(position, action):
        dx, dy = Actions.direction_to_vector(action)
        x, y = position

        return x + dx, y + dy

    @staticmethod
    def direction_to_vector(direction, speed=1.0):
        dx, dy = Actions.directions[direction]
        return dx * speed, dy * speed

    @staticmethod
    def vector_to_direction(vector):
        dx, dy = vector

        if dy > 0:
            return Direction.NORTH

        if dy < 0:
            return Direction.SOUTH

        if dx > 0:
            return Direction.EAST

        if dx < 0:
            return Direction.WEST

        return Direction.STOP

    @staticmethod
    def reverse_direction(action):
        if action == Direction.NORTH:
            return Direction.SOUTH

        if action == Direction.SOUTH:
            return Direction.NORTH

        if action == Direction.EAST:
            return Direction.WEST

        if action == Direction.WEST:
            return Direction.EAST

        return action
