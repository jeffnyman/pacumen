import sys
import logging
import argparse
import textwrap

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
    """

    core_opt = parser.add_argument_group(title='core options', description=textwrap.dedent(core_opt_desc))

    core_opt.add_argument("-l", "--layout", dest="layout", default="test_maze", help=argparse.SUPPRESS)

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

    return args


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
