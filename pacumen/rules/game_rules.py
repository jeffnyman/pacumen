from pacumen.mechanics.game import Game
from pacumen.mechanics.game_state import GameState


class GameRules:
    def new_game(self, layout, pacman_agent, ghost_agents, display, quiet=False):
        """
        A new game means establishing a GameState (which will in turn
        establish GameStateData). This is creating the initial starting
        state of the game. That state is provided as a property on the
        game instance. Note that setting up the GameStateData, as part
        of this process, will also set up AgentState objects.
        """
        agents = [pacman_agent] + ghost_agents[:layout.get_ghost_count()]

        start_state = GameState()
        start_state.initialize(layout, len(ghost_agents))

        game = Game(agents, display, self)
        game.state = start_state
        self.initial_state = start_state.deep_copy()

        self.quiet = quiet

        return game

    def process(self, state, game):
        if state.is_win():
            self.win(state, game)

        if state.is_loss():
            self.lose(state, game)

    def win(self, state, game):
        if not self.quiet:
            print("Pacumen wins! Score: %d" % state.data.score)

        game.game_over = True

    def lose(self, state, game):
        if not self.quiet:
            print("Pacumen lost! Score: %d" % state.data.score)

        game.game_over = True

    def get_progress(self, game):
        return float(game.state.get_num_dots()) / self.initial_state.get_num_dots()

    @staticmethod
    def agent_crash(agent_index):
        if agent_index == 0:
            print("Pacumen crashed")
        else:
            print("A ghost crashed")

    def __init__(self):
        self.quiet = None
        self.initial_state = None
