from pacumen.library.utilities import raise_not_defined


class SearchProblem:
    # noinspection PyMethodMayBeStatic
    def get_start_state(self):
        raise_not_defined()

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def is_goal_state(self, state):
        raise_not_defined()

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def get_successors(self, state):
        raise_not_defined()

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def get_cost_of_actions(self, actions):
        raise_not_defined()
