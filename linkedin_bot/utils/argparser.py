from argparse import ArgumentParser, Namespace

SYS_ARGS = dict(
    debug='Enable debug mode',
)


def _add_args_to_parser(parser: ArgumentParser, arguments: dict[str, str]) -> None:
    for arg, help_text in arguments.items():
        parser.add_argument(f'--{arg}', action='store_true', help=help_text)


def check_sys_arg() -> Namespace:
    """
    Parse CLI arguments.

    Returns:
        Namespace: Parsed arguments.
    """
    parser: ArgumentParser = ArgumentParser()
    _add_args_to_parser(parser, SYS_ARGS)
    return parser.parse_args()
