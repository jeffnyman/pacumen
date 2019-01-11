import time
from pacumen.library.utilities import nearest_point

DRAW_EVERY_STEP = 1
DISPLAY_MOVES = False
SLEEP_TIME = 0


class NoDisplay:
    def initialize(self, state):
        pass

    def update(self, state):
        pass

    @staticmethod
    def finish():
        pass


class PacmanDisplay:
    def initialize(self, state):
        self.draw_display(state)
        self.pause_display()
        self.turn = 0
        self.agent_counter = 0

    def update(self, state):
        num_agents = len(state.agent_states)
        self.agent_counter = (self.agent_counter + 1) % num_agents

        if self.agent_counter == 0:
            self.turn += 1

            if DISPLAY_MOVES:
                ghosts = [nearest_point(state.agent_states[i].get_position()) for i in range(1, num_agents)]
                print("%4d) P: %-8s" %
                      (self.turn, str(nearest_point(state.agent_states[0].get_position()))),
                      '| Score: %-5d' % state.score, '| Ghosts:', ghosts)

            if self.turn % DRAW_EVERY_STEP == 0:
                self.draw_display(state)
                self.pause_display()

        if state.check_for_win() or state.check_for_loss():
            self.draw_display(state)

    @staticmethod
    def draw_display(state):
        print(state)

    @staticmethod
    def pause_display():
        time.sleep(SLEEP_TIME)

    @staticmethod
    def finish():
        pass

    def __init__(self):
        self.turn = 0
        self.agent_counter = 0
