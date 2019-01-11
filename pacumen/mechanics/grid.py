class Grid:
    def as_list(self, key=True):
        """
        Returns a list of grid positions from the current grid, based on
        the key value.
        """
        grid_list = []

        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    grid_list.append((x, y))

        return grid_list

    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    def copy(self):
        """
        A grid like this:

            FFFF
            FTFF

        Would return this:

            [[False, False, False, False], [False, True, False, False]]
        """
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deep_copy(self):
        return self.copy()

    def shallow_copy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def __init__(self, width, height, initial_value=False):
        if initial_value not in [False, True]:
            raise Exception("Grids can only contain boolean values.")

        self.width = width
        self.height = height

        self.data = [[initial_value for _ in range(height)] for _ in range(width)]

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __getitem__(self, item):
        return self.data[item]

    def __hash__(self):
        """
        The hash for a grid will be given in powers of 2. That value will
        then be added to a hash_value being stored for each element of
        the grid that is marked True. For example, consider the following
        grid of dots

        FFFFFFFFFF
        FTTFFFFFFF
        FFFFFFFFFF

        Here there are two True elements, so those would be given hash_value
        and base values accordingly:

        True 0 16
        True 16 128

        The hash for that grid would then be the addition of both: 144.
        """
        base = 1
        hash_value = 0

        for row in self.data:
            for element in row:
                if element:
                    hash_value += base

                base *= 2

        return hash(hash_value)

    def __eq__(self, other):
        if other is None:
            return False

        return self.data == other.data
