import sys
import traceback


class Game:
    PREVIOUS_STDOUT = None
    PREVIOUS_STDERR = None

    def run(self):
        """
        This is the core logic of the entire program. Here is where the game
        loop is entered. That look is only entered after the game display
        has been established with an initial set of game state data.
        """
        self.display.initialize(self.state.data)

        # Inform learning agents of the game start. This allows for the call
        # for processing the initial state.

        for index in range(len(self.agents)):
            agent = self.agents[index]

            if not agent:
                self.mute_output(index)
                sys.stderr.write("Agent %d failed to load" % index)
                self.unmute_output()
                self._agent_crash(index, quiet=True)
                return

            if 'process_initial_state' in dir(agent):
                self.mute_output(index)

                agent.process_initial_state(self.state.deep_copy())

                self.unmute_output()

        agent_index = self.starting_agent
        number_of_agents = len(self.agents)

        while not self.game_over:
            # Agents will be iterated through so that each has a "turn"
            # during game play.
            agent = self.agents[agent_index]

            # Get an observation of the environment state.

            if 'observation_function' in dir(agent):
                self.mute_output(agent_index)

                observation = agent.observation_function(self.state.deep_copy())

                self.unmute_output()
            else:
                observation = self.state.deep_copy()

            # Each agent will get an action based on the current observation.
            # That action will be appended to the move history which allows a
            # complete reconstruction of the world based on the actions taken
            # by each agent.

            self.mute_output(agent_index)

            action = agent.get_action(observation)

            self.unmute_output()

            self.move_history.append((agent_index, action))

            # A new environment state is achieved by executing the action
            # against the current environment. This generates a successor
            # state which provides an updated observation to the agents.

            self.state = self.state.generate_successor(agent_index, action)

            # Change the display of the environment to indicate
            # the successor state.

            self.display.update(self.state.data)

            # Any rules that are applicable to the game generally have to
            # processed. This is usually checking for specific termination
            # conditions.

            self.rules.process(self.state, self)

            # Track the progress of moves. In this context, one move consists
            # of a turn by each agent. So in a context when there are two
            # agents, each agent will have a turn and a "move" refers to each
            # of those turns. The term "ply" refers to one turn taken by one
            # of the agents.

            if agent_index == number_of_agents + 1:
                self.number_of_moves += 1

            # Cycle through the agents so that each agent gets a turn.
            agent_index = (agent_index + 1) % number_of_agents

        # Inform a learning agent of the game result. This is allowing
        # the agent to deal with terminal states in some way.

        for agent_index, agent in enumerate(self.agents):
            if "terminal_state" in dir(agent):
                try:
                    self.mute_output(agent_index)

                    agent.terminal_state(self.state)

                    self.unmute_output()
                except RuntimeError:
                    self._agent_crash(agent_index)
                    self.unmute_output()
                    return

        self.display.finish()

    def get_progress(self):
        if self.game_over:
            return 1.0
        else:
            return self.rules.get_progress(self)

    def mute_output(self, agent_index):
        if not self.mute_agents:
            return

        global PREVIOUS_STDOUT, PREVIOUS_STDERR

        PREVIOUS_STDOUT = sys.stdout
        PREVIOUS_STDERR = sys.stderr

        sys.stdout = self.agent_output[agent_index]
        sys.stderr = self.agent_output[agent_index]

    def unmute_output(self):
        if not self.mute_agents:
            return

        global PREVIOUS_STDOUT, PREVIOUS_STDERR

        sys.stdout = PREVIOUS_STDOUT
        sys.stderr = PREVIOUS_STDERR

    def _agent_crash(self, agent_index, quiet=False):
        if not quiet:
            traceback.print_exc()

        self.game_over = True
        self.agent_crashed = True
        self.rules.agent_crash(self, agent_index)

    def __init__(self, agents, display, rules, starting_agent=0, mute_agents=False):
        self.agents = agents
        self.display = display
        self.rules = rules
        self.starting_agent = starting_agent
        self.state = None
        self.game_over = False
        self.move_history = []
        self.agent_crashed = False
        self.mute_agents = mute_agents
        self.number_of_moves = None

        from io import StringIO
        self.agent_output = [StringIO() for _ in agents]
