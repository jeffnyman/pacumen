from pacumen.library.utilities import raise_not_defined


class Agent:
    def __init__(self, index=0):
        self.index = index

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def get_action(self, state):
        """
        This method for any agent will receive a GameState object. The actual
        implementation falls to the object instance but in all cases this
        method should return a Direction action.
        """
        raise_not_defined()
