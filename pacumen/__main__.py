import sys
import argparse
import textwrap


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
            
                python pacumen.py <options>
            """
        ),
        epilog=textwrap.dedent(
            """
            Enjoy Pacumen!
            """
        )
    )

    options = parser.parse_args(arguments)

    return options


if __name__ == '__main__':
    kwargs = process_command(sys.argv[1:])
