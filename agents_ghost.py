from pacumen.mechanics.agent import Agent
from pacumen.mechanics.agent_action import Actions
from pacumen.library.counter import Counter
from pacumen.mechanics.agent_direction import Direction
from pacumen.library.utilities import raise_not_defined, choose_from_distribution, manhattan_distance


class GhostAgent(Agent):
    def __init__(self, index):
        self.index = index

        super().__init__(index)

    def get_action(self, state):
        distribution = self.get_distribution(state)

        # noinspection PyTypeChecker
        if len(distribution) == 0:
            return Direction.STOP
        else:
            return choose_from_distribution(distribution)

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def get_distribution(self, state):
        """
        This method must return a Counter that encodes a distribution over
        actions from the provided state. This must be implemented by any
        ghost agent.
        """
        raise_not_defined()


class RandomGhost(GhostAgent):
    """
    A ghost that chooses a legal action uniformly at random.
    """
    def get_distribution(self, state):
        distribution = Counter()

        for action in state.get_legal_actions(self.index):
            distribution[action] = 1.0

        distribution.normalize()

        return distribution


class DirectionalGhost(GhostAgent):
    """
    A ghost that will try to rush at Pacumen but will flee when scared.
    """
    def __init__(self, index, prob_attack=0.8, prob_scared_flee=0.8):
        self.prob_attack = prob_attack
        self.prob_scared_flee = prob_scared_flee

        super().__init__(index)

    def get_distribution(self, state):
        ghost_state = state.get_ghost_state(self.index)
        legal_actions = state.get_legal_actions(self.index)
        position = state.get_ghost_position(self.index)
        is_scared = ghost_state.scared_timer > 0

        speed = 1

        if is_scared:
            speed = 0.5

        action_vectors = [Actions.direction_to_vector(a, speed) for a in legal_actions]
        new_positions = [(position[0] + a[0], position[1] + a[1]) for a in action_vectors]
        pacumen_position = state.get_pacumen_position()

        # Select best actions given the state.
        pacumen_distance = [manhattan_distance(pos, pacumen_position) for pos in new_positions]

        if is_scared:
            best_score = max(pacumen_distance)
            best_prob = self.prob_scared_flee
        else:
            best_score = min(pacumen_distance)
            best_prob = self.prob_attack

        best_actions = [action for action, distance in zip(legal_actions, pacumen_distance) if distance == best_score]

        # Construct distribution.
        distribution = Counter()

        for a in best_actions:
            distribution[a] = best_prob / len(best_actions)

        for a in legal_actions:
            distribution[a] += (1 - best_prob) / len(legal_actions)

        distribution.normalize()

        return distribution
