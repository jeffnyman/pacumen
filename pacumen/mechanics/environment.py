from pacumen.library.utilities import abstract


class Environment:
    """
    Provides an abstract class for environments in which Markov decision
    process formulations are carried out.
    """

    # noinspection PyMethodMayBeStatic
    def get_current_state(self):
        """
        Returns the current state of the environment.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def get_possible_actions(self, _state):
        """
        Returns the possible actions an agent can take in the given state.
        An empty list is returned if the environment is in a terminal state.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def reset(self):
        """
        Returns the environment to its start state.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def do_action(self, _action):
        """
        Performs the given action in the current environment state and
        updates the environment. Returns a (reward, next_state) pair.
        """
        abstract()

    def is_terminal(self):
        """
        Checks if the environment has entered a terminal state. This means
        there are no successors.
        """
        # noinspection PyNoneFunctionAssignment
        state = self.get_current_state()

        # noinspection PyNoneFunctionAssignment
        actions = self.get_possible_actions(state)

        # noinspection PyTypeChecker
        return len(actions) == 0
