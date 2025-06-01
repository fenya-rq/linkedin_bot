from argparse import ArgumentParser, Namespace

SYS_ARGS = {
    'posts_restrict': {'type': int, 'help': 'Number of reposts', 'default': 3},
    'debug': {'type': str, 'help': 'Enable debug mode', 'default': 'false'},
}


def _add_args_to_parser(parser: ArgumentParser, arguments: dict[str, dict]) -> None:
    """
    Add arguments to the parser.

    :param parser: ArgumentParser instance
    :param arguments: Dictionary of arguments to add
    """
    for arg, arg_props in arguments.items():
        parser.add_argument(
            f'--{arg}',
            type=arg_props.get('type', str),
            help=arg_props.get('help', ''),
            default=arg_props.get('default'),
        )


def check_sys_arg() -> Namespace:
    """
    Parse CLI arguments.

    :returns: Parsed arguments
    """
    parser: ArgumentParser = ArgumentParser()
    _add_args_to_parser(parser, SYS_ARGS)
    return parser.parse_args()
