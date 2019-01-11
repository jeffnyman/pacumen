import os
import sys
import random
import logging
import argparse
import textwrap
import importlib

from pacumen.mechanics import layout
from pacumen.rules.game_rules import GameRules


if sys.version_info < (3, 0):
    sys.stderr.write("Pacumen requires Python 3.\n")
    sys.exit(1)


def run_game(game_layout, pacumen, ghosts, game_display, num_games, num_training=0, record_actions=False):
    """
    This method is the actual starting point for execution of a game, taking
    in many values that were passed in as options from the command line. To
    run a game requires creating a new game, based on certain game rules.
    """
    # noinspection PyUnresolvedReferences
    import __main__
    __main__.__dict__['board_display'] = game_display

    rules = GameRules()
    games = []

    for play_session in range(num_games):
        quiet_execution = play_session < num_training

        if quiet_execution:
            from pacumen.displays import textual_pacman
            display = textual_pacman.NoDisplay()
            rules.quiet = True
        else:
            display = game_display
            rules.quiet = False

        game = rules.new_game(game_layout, pacumen, ghosts, display, quiet_execution)
        game.run()

        if not quiet_execution:
            games.append(game)

        if record_actions:
            import time
            import pickle

            file_name = ('recorded-game-%d' % (play_session + 1)) + '-'.join([str(t) for t in time.localtime()[1:6]])
            f = open(file_name, 'wb')
            components = {'game_layout': game_layout, 'game_actions': game.move_history}
            pickle.dump(components, f)
            f.close()

    if num_games - num_training > 0:
        scores = [game.state.get_score() for game in games]
        wins = [game.state.is_win() for game in games]
        win_rate = wins.count(True) / float(len(wins))

        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))
        print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), win_rate))
        print('Record:       ', ', '.join([['Loss', 'Win'][int(w)] for w in wins]))

    return games


def replay_game(game_layout, game_actions, game_display):
    from agents_ghost import RandomGhost
    from agents_pacumen import GreedyAgent

    rules = GameRules()

    # noinspection PyTypeChecker
    agents = [GreedyAgent()] + [RandomGhost(i + 1) for i in range(game_layout.get_ghost_count())]

    game = rules.new_game(game_layout, agents[0], agents[1:], game_display)
    state = game.state

    game_display.initialize(state.data)

    for action in game_actions:
        state = state.generate_successor(*action)
        game_display.update(state.data)
        rules.process(state, game)

    game_display.finish()


def process_command(arguments):
    """
    Processes the command line used to run pacumen. The command line can
    contain a series of options which will determine how the pacumen
    implementation executes.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Pacumen Runner",
        usage=textwrap.dedent(
            """
            The general format is:
            
                pacumen <options>
                
            Examples:
            
                (1) pacumen
                    - starts an interactive game
                    
                (2) pacumen --layout small_classic --zoom 2
                    - starts an interactive game on a smaller board, zoomed in
            """
        ),
        epilog=textwrap.dedent(
            """
            Enjoy Pacumen!
            """
        )
    )

    core_opt_desc = """
    -l, --layout <layout_file>   the layout_file providing the environment (default: test_maze).
    
    -p, --pacman <agent>         the agent name to use for Pac-Man (default: HumanAgent).
    
    -g, --ghost <agent>          the agent type to use for the ghosts (default: RandomGhost).
    
    -a, --agentArgs <values>     comma separated values sent to agent; e.g. "opt1=val1,opt2,opt3=val3"
    """

    core_opt = parser.add_argument_group(title='core options', description=textwrap.dedent(core_opt_desc))

    core_opt.add_argument("-l", "--layout", dest="layout", default="test_maze", help=argparse.SUPPRESS)

    core_opt.add_argument("-p", "--pacman", dest="pacman", default="HumanAgent", help=argparse.SUPPRESS)

    core_opt.add_argument("-g", "--ghost", dest="ghost", default="RandomGhost", help=argparse.SUPPRESS)

    core_opt.add_argument("-a", "--agentArgs", dest="agent_args", help=argparse.SUPPRESS)

    # ==============

    learn_opt_desc = """
    -n, --numGames <number>      the number of games to play (default: 1).
    
    -x, --numTraining <number>   number of training episodes; this suppresses output (default: 0).
    
    -t, --textDisplay            display game output as text only.
    
    -q, --quiet                  generate minimal output, no display.
    """

    learn_opt = parser.add_argument_group(title='learning options', description=textwrap.dedent(learn_opt_desc))

    learn_opt.add_argument("-n", "--numGames", dest="num_games", type=int, default=1, help=argparse.SUPPRESS)

    learn_opt.add_argument("-x", "--numTraining", dest="num_training", type=int, default=0, help=argparse.SUPPRESS)

    learn_opt.add_argument("-t", "--textDisplay", dest="text_display", default=False, action="store_true",
                           help=argparse.SUPPRESS)

    learn_opt.add_argument("-q", "--quiet", dest="quiet_display", default=False, action="store_true",
                           help=argparse.SUPPRESS)

    # ==============

    env_opt_desc = """
    -k, --numGhosts <number>     the maximum number of ghosts (default: 4).
    
    -f, --frameTime <value>      time to delay between frames; < 0 means keyboard (default: 0.1).
    
    -z, --zoom <value>           control the size of the graphical display (default: 1.0).
    
    -r, --recordActions          writes game histories to a file, named by timestamp.
    
    --replayActions              runs a recorded game file to replay actions.
    
    --fixRandomSeed              sets a random seed to always play the same game.
    """

    env_opt = parser.add_argument_group(title='environment options', description=textwrap.dedent(env_opt_desc))

    env_opt.add_argument("-k", "--numGhosts", dest="num_ghosts", type=int, default=4, help=argparse.SUPPRESS)

    env_opt.add_argument("-f", "--frameTime", dest="frame_time", type=float, default=0.1, help=argparse.SUPPRESS)

    env_opt.add_argument("-z", "--zoom", dest="zoom", type=float, default=1.0, help=argparse.SUPPRESS)

    env_opt.add_argument("-r", "--recordActions", dest="record_actions", default=False, action="store_true",
                         help=argparse.SUPPRESS)

    env_opt.add_argument("--replayActions", dest="replay_actions", default=None, help=argparse.SUPPRESS)

    env_opt.add_argument("--fixRandomSeed", dest="fix_random_seed", default=False, action="store_true",
                         help=argparse.SUPPRESS)

    # ==============

    logging_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    verify_functions = ["layout", "game_state", "graphical_builder", "graphical_pacman"]

    parser.add_argument("--verify", dest="verify", default=None,
                        choices=verify_functions, metavar='',
                        help="verify aspects of functionality; allowed values: " +
                             ", ".join(verify_functions) + " (default: %(default)s)")

    parser.add_argument("-v", "--verbose", dest="log_level", default="WARNING",
                        choices=logging_levels, metavar='',
                        help="increase output verbosity; allowed values: " +
                             ", ".join(logging_levels) + " (default: %(default)s)")

    # ==============

    options = parser.parse_args(arguments)
    args = dict()

    logging.basicConfig(level=logging.getLevelName(options.log_level), format="%(message)s")

    if options.verify:
        verify_functionality(arguments[1])
        sys.exit(1)

    if options.fix_random_seed:
        random.seed('pacumen')

    # A game layout has to be specified and found. This is a bare minimum
    # starting condition. Without a layout, which corresponds to a game
    # board, there will be nowhere to place an agent.

    args['game_layout'] = layout.get_layout(options.layout)

    if args['game_layout'] is None:
        raise Exception("The layout " + options.layout + " could not be found.")

    # A pacumen agent has to be loaded. Any agent options that were specified
    # must be sent to this agent object.

    not_human = options.replay_actions is None and (options.text_display or options.quiet_display)
    pacman_type = load_agent(options.pacman, not_human)
    agent_opts = parse_agent_options(options.agent_args)

    if options.num_training > 0:
        args['num_training'] = options.num_training
        if 'num_training' not in agent_opts:
            agent_opts['num_training'] = options.num_training

    try:
        pacman = pacman_type(**agent_opts)
    except TypeError:
        # noinspection PyUnusedLocal
        pacman = None
        print("PROBLEM: An argument that you used on the command line to")
        print("control some aspect of the agent can't be used. Likely")
        print("this is due to using a parameter on an agent that does")
        print("not support that parameter.\n\n")
        raise

    args['pacumen'] = pacman

    # Load a ghost agent. There can be multiple ghosts in a game but only
    # one type of ghost agent.

    ghost_type = load_agent(options.ghost, not_human)
    args['ghosts'] = [ghost_type(i + 1) for i in range(options.num_ghosts)]

    # Provide a display for the environment.

    if options.quiet_display:
        from pacumen.displays import textual_pacman
        args['game_display'] = textual_pacman.NoDisplay()
    elif options.text_display:
        from pacumen.displays import textual_pacman
        textual_pacman.SLEEP_TIME = options.frame_time
        args['game_display'] = textual_pacman.PacmanDisplay()
    else:
        from pacumen.displays import graphical_pacman
        args['game_display'] = graphical_pacman.PacmanDisplay(zoom=options.zoom, frame_time=options.frame_time)

    args['num_games'] = options.num_games
    args['record_actions'] = options.record_actions

    # Recorded games don't use the run_game method or the argument structure.

    if options.replay_actions is not None:
        print('Replaying recorded game %s.' % options.replay_actions)

        try:
            import pickle
        except ImportError:
            raise Exception("Pickle not installed.")

        f = open(options.replay_actions)

        try:
            with open(options.replay_actions, 'rb') as f:
                recorded = pickle.load(f)
        finally:
            f.close()

        recorded['game_display'] = args['game_display']
        replay_game(**recorded)
        sys.exit(0)

    return args


def load_agent(pacman, not_human):
    sys.path.insert(0, os.getcwd())

    python_path_string = os.path.expandvars("$PYTHONPATH")

    if python_path_string.find(';') == -1:
        python_path_dirs = python_path_string.split(':')
    else:
        python_path_dirs = python_path_string.split(';')

    # noinspection PyTypeChecker
    python_path_dirs.append(os.getcwd())

    for module_dir in python_path_dirs:
        if not os.path.isdir(module_dir):
            continue

        # noinspection PyTypeChecker
        module_names = [f for f in os.listdir(module_dir) if f.startswith('agents_')]

        for module_name in module_names:
            try:
                agent_module = importlib.import_module(module_name[:-3])
            except ImportError:
                continue

            if pacman in dir(agent_module):
                if not_human and module_name == "agents_human.py":
                    raise Exception("Using the human agent requires the graphical display.")

                return getattr(agent_module, pacman)

    raise Exception("The agent " + pacman + " is not specified in any agents_*.py file.")


def parse_agent_options(option_string):
    if option_string is None:
        return {}

    parts = option_string.split(',')
    options = {}

    for part in parts:
        if '=' in part:
            key, value = part.split('=')
        else:
            key, value = part, 1

        options[key] = value

    return options


def verify_layout():
    from pacumen.mechanics import layout
    layout.test()


def verify_game_state():
    from pacumen.mechanics import game_state
    game_state.test()


def verify_graphical_builder():
    from pacumen.displays import graphical_builder
    graphical_builder.test()


def verify_graphical_pacman():
    from pacumen.displays import graphical_pacman
    graphical_pacman.test()


def verify_functionality(argument):
    options = {
        "graphical_pacman": verify_graphical_pacman,
        "graphical_builder": verify_graphical_builder,
        "game_state": verify_game_state,
        "layout": verify_layout
    }

    try:
        options[argument]()
    except IndexError:
        print("Provide a valid test function name.")
    except KeyError as key_name:
        print("Unable to execute test function:", key_name)


def main():
    kwargs = process_command(sys.argv[1:])
    run_game(**kwargs)


if __name__ == '__main__':
    main()
