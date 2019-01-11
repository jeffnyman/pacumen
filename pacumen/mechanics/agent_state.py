class AgentState:
    def get_position(self):
        if self.configuration is None:
            return None

        return self.configuration.get_position()

    def get_direction(self):
        if self.configuration is None:
            return None

        return self.configuration.get_direction()

    def copy(self):
        state = AgentState(self.start, self.is_pacumen)
        state.configuration = self.configuration
        state.scared_timer = self.scared_timer
        return state

    def __init__(self, starting_configuration, is_pacumen):
        self.configuration = starting_configuration
        self.start = starting_configuration
        self.is_pacumen = is_pacumen
        self.scared_timer = 0

    def __str__(self):
        if self.is_pacumen:
            return "Pacumen: " + str(self.configuration)
        else:
            return "Ghost: " + str(self.configuration)

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scared_timer))

    def __eq__(self, other):
        if other is None:
            return False

        return self.configuration == other.configuration and self.scared_timer == other.scared_timer
