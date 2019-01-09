import os
import sys
import logging
import argparse
import textwrap
import importlib

from pacumen.mechanics import layout

if sys.version_info < (3, 0):
    sys.stderr.write("Pacumen requires Python 3.\n")
    sys.exit(1)


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
    """

    core_opt = parser.add_argument_group(title='core options', description=textwrap.dedent(core_opt_desc))

    core_opt.add_argument("-l", "--layout", dest="layout", default="test_maze", help=argparse.SUPPRESS)

    core_opt.add_argument("-p", "--pacman", dest="pacman", default="HumanAgent", help=argparse.SUPPRESS)

    core_opt.add_argument("-a", "--agentArgs", dest="agent_args", help=argparse.SUPPRESS)

    # ==============

    logging_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    verify_functions = ["layout"]

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

    # A game layout has to be specified and found. This is a bare minimum
    # starting condition. Without a layout, which corresponds to a game
    # board, there will be nowhere to place an agent.

    args['game_layout'] = layout.get_layout(options.layout)

    if args['game_layout'] is None:
        raise Exception("The layout " + options.layout + " could not be found.")

    # A pacumen agent has to be loaded. Any agent options that were specified
    # must be sent to this agent object.

    pacman_type = load_agent(options.pacman, False)
    agent_opts = parse_agent_options(options.agent_args)

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

    return args


def load_agent(pacman, not_human):
    python_path_string = os.path.expandvars("$PYTHONPATH")

    if python_path_string.find(';') == -1:
        python_path_dirs = python_path_string.split(':')
    else:
        python_path_dirs = python_path_string.split(';')

    # noinspection PyTypeChecker
    python_path_dirs.append('.')
    python_path_dirs.append(os.getcwd())
    python_path_dirs.append(os.getcwd() + "/agents")

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


def verify_functionality(argument):
    options = {
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


if __name__ == '__main__':
    main()
