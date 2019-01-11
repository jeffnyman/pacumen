from pacumen.mechanics.agent import Agent
from pacumen.mechanics.agent_direction import Direction


class HumanAgent(Agent):
    """
    An agent controlled by a human using a keyboard.
    """
    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index=0):
        self.index = index
        self.keys = []
        self.last_move = Direction.STOP

        super().__init__(index)

    def get_action(self, state):
        from pacumen.displays.graphical_builder import keys_waiting
        from pacumen.displays.graphical_builder import keys_pressed

        keys = keys_waiting() + keys_pressed()

        if keys:
            self.keys = keys

        legal_actions = state.get_legal_actions(self.index)
        action = self.get_movement(legal_actions)

        if action == Direction.STOP:
            # Try to move in the same direction as the previous move.
            if self.last_move in legal_actions:
                action = self.last_move

        self.last_move = action

        return action

    def get_movement(self, legal_actions):
        movement = Direction.STOP

        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Direction.WEST in legal_actions:
            movement = Direction.WEST

        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Direction.EAST in legal_actions:
            movement = Direction.EAST

        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Direction.NORTH in legal_actions:
            movement = Direction.NORTH

        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Direction.SOUTH in legal_actions:
            movement = Direction.SOUTH

        return movement
