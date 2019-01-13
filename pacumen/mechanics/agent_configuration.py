from pacumen.mechanics.agent_action import Actions
from pacumen.mechanics.agent_direction import Direction


class Configuration:
    def generate_successor(self, vector):
        x, y = self.position
        dx, dy = vector
        direction = Actions.vector_to_direction(vector)

        # There is no 'stop' direction so if that's the direction that gets
        # returned, it's necessary to fall back to the current direction.
        if direction == Direction.STOP:
            direction = self.direction

        return Configuration((x + dx, y + dy), direction)

    def get_position(self):
        return self.position

    def get_direction(self):
        return self.direction

    def is_integer(self):
        x, y = self.position
        return x == int(x) and y == int(y)

    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

    def __str__(self):
        return "(x,y)=" + str(self.position) + ", " + str(self.direction)

    def __hash__(self):
        x = hash(self.position)
        y = hash(self.direction)

        return hash(x + 13 * y)

    def __eq__(self, other):
        if other is None:
            return False

        return self.position == other.position and self.direction == other.direction
