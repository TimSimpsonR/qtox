import argparse

from . import toxini


def main() -> None:
    parser = argparse.ArgumentParser("qtox")
    parser.add_argument(
        "-c", help="Directory containing tox.ini", type=str, default=None
    )
    parser.add_argument(
        "--envs",
        help="List of environments, in the order you want qtox to show them "
        "(defaults to using envlist specified at top of tox.ini file",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    ini = toxini.get_ini(args.c)

    print(ini.toxinidir)
