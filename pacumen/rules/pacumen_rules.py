import sys
from pacumen.mechanics.agent_action import Actions
from pacumen.library.utilities import nearest_point, manhattan_distance


class PacumenRules:
    """
    The methods in this class govern how the Pacumen agent interacts with
    the environment under the basic game rules.
    """
    PACUMEN_SPEED = 1

    # Moves ghosts are scared.
    SCARED_TIME = 40

    @staticmethod
    def get_legal_actions(state):
        """
        Based on the current configuration of Pacumen as well as the walls,
        as provided by the layout, a list of possible actions is returned.
        """
        return Actions.get_possible_actions(state.get_pacumen_state().configuration, state.data.layout.walls)

    @staticmethod
    def apply_action(state, action):
        """
        Edits the environment state to reflect the results of an action. The
        specific aspects of the environment state that are modified are where
        Pacumen ends up and whether it consumes anything in that new position.
        """
        legal_actions = PacumenRules.get_legal_actions(state)

        if action not in legal_actions:
            sys.tracebacklimit = 0
            print("Pacumen tried to go '" + str(action) + "' but that action was")
            print("not one of the allowed actions from that point.")
            print("Here is what the environment looked like when")
            print("the action was attempted:\n")
            print(state)
            raise Exception("Illegal action attempted.")

        pacumen_state = state.data.agent_states[0]

        vector = Actions.direction_to_vector(action, PacumenRules.PACUMEN_SPEED)

        pacumen_state.configuration = pacumen_state.configuration.generate_successor(vector)

        next_position = pacumen_state.configuration.get_position()
        nearest_position = nearest_point(next_position)

        if manhattan_distance(nearest_position, next_position) <= 0.5:
            PacumenRules.consume(nearest_position, state)

    @staticmethod
    def consume(position, state):
        x, y = position

        # Eat food pellet.
        if state.data.dots[x][y]:
            state.data.score_change += 10
            state.data.dots = state.data.dots.copy()
            state.data.dots[x][y] = False

            state.data.set_dot_eaten_location(position)

            num_dots = state.get_num_dots()

            if num_dots == 0 and not state.data.check_for_loss():
                state.data.score_change += 500
                state.data.is_a_win()

        # Eat power pellet.
        if position in state.get_pellets():
            state.data.pellets.remove(position)
            state.data.set_pellet_eaten_location(position)

            # Reset all ghosts' scared timers.
            for index in range(1, len(state.data.agent_states)):
                state.data.agent_states[index].scared_timer = PacumenRules.SCARED_TIME
