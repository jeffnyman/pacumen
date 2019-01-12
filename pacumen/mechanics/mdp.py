from pacumen.library.utilities import abstract


class MarkovDecisionProcess:
    """
    Provides methods that are relevant for any Markov decision process.
    """

    # noinspection PyMethodMayBeStatic
    def get_start_state(self):
        """
        Provides the starting state of the MDP.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def get_states(self):
        """
        Provides a list of all states in the MDP. Note that for very
        large MDPs this may not possible.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def get_possible_actions(self, _state):
        """
        Provides a list of possible actions from the provided state.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def get_transition_states_and_probs(self, _state, _action):
        """
        Returns a list of (next_state, prob) pairs representing the states
        reachable from 'state' by taking 'action' along with their transition
        probabilities.

        Note that in Q-Learning and reinforcement learning in general, we
        won't know these probabilities nor do we directly model them.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def get_reward(self, _state, _action, _next_state):
        """
        Gets the reward for the state, action, next_state transition.

        Note that this is not available in reinforcement learning.
        """
        abstract()

    # noinspection PyMethodMayBeStatic
    def is_terminal(self, _state):
        """
        Returns true if the current state is a terminal state.

        Note that, by convention, a terminal state has zero future rewards.
        It's possible that the terminal state(s) have no possible actions.
        It's  also common to think of the terminal state as having a type of
        self-loop action 'pass' with zero reward. Those formulations are
        essentially equivalent.
        """
        abstract()
