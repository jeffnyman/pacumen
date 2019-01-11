from pacumen.mechanics.agent_action import Actions
from pacumen.mechanics.agent_direction import Direction
from pacumen.library.utilities import nearest_point, manhattan_distance


class GhostRules:
    """
    This class provides functions that dictate how ghosts interact with the
    environment. In general, ghosts can't stop and they can't turn around
    unless they reach a dead end. This means once a ghost picks a direction,
    it will keep moving in that direction. Ghosts can turn 90 degrees at
    intersections.
    """
    GHOST_SPEED = 1.0

    # How close ghosts must be to Pacumen to eat him.
    COLLISION_TOLERANCE = 0.7

    @staticmethod
    def get_legal_actions(state, ghost_index):
        config = state.get_ghost_state(ghost_index).configuration
        possible_actions = Actions.get_possible_actions(config, state.data.layout.walls)
        reverse = Actions.reverse_direction(config.direction)

        if Direction.STOP in possible_actions:
            possible_actions.remove(Direction.STOP)

        if reverse in possible_actions and len(possible_actions) > 1:
            possible_actions.remove(reverse)

        return possible_actions

    @staticmethod
    def apply_action(state, action, ghost_index):
        legal_actions = GhostRules.get_legal_actions(state, ghost_index)

        if action not in legal_actions:
            raise Exception("Illegal ghost action " + str(action))

        ghost_state = state.data.agent_states[ghost_index]
        speed = GhostRules.GHOST_SPEED

        if ghost_state.scared_timer > 0:
            speed /= 2.0

        vector = Actions.direction_to_vector(action, speed)
        ghost_state.configuration = ghost_state.configuration.generate_successor(vector)

    @staticmethod
    def decrement_timer(ghost_state):
        timer = ghost_state.scared_timer

        if timer == 1:
            ghost_state.configuration.position = nearest_point(ghost_state.configuration.position)

        ghost_state.scared_timer = max(0, timer - 1)

    @staticmethod
    def check_for_collision(state, agent_index):
        pacman_position = state.get_pacumen_position()

        if agent_index == 0:
            for index in range(1, len(state.data.agent_states)):
                ghost_state = state.data.agent_states[index]
                ghost_position = ghost_state.configuration.get_position()

                if GhostRules.can_eat_pacumen(pacman_position, ghost_position):
                    GhostRules.collide(state, ghost_state, index)
        else:
            ghost_state = state.data.agent_states[agent_index]
            ghost_position = ghost_state.configuration.get_position()

            if GhostRules.can_eat_pacumen(pacman_position, ghost_position):
                GhostRules.collide(state, ghost_state, agent_index)

    @staticmethod
    def can_eat_pacumen(pacman_position, ghost_position):
        return manhattan_distance(ghost_position, pacman_position) <= GhostRules.COLLISION_TOLERANCE

    @staticmethod
    def collide(state, ghost_state, agent_index):
        if ghost_state.scared_timer > 0:
            state.data.score_change += 200
            GhostRules.spawn_ghost(state, ghost_state)
            ghost_state.scared_timer = 0
            state.data.eaten[agent_index] = True
        else:
            if not state.data.check_for_win():
                state.data.score_change -= 500
                state.data.is_a_loss()

    @staticmethod
    def spawn_ghost(state, ghost_state):
        ghost_state.configuration = ghost_state.start
