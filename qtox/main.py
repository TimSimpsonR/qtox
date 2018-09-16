import enum
import sys
import typing as t

from . import bash
from . import toxini


USAGE = """
Usage: qtox [-c tox_directory] --envs env1 [env2 env3 ...]

Arguments:
    -c tox_directory    Directory containing tox.ini.
    -e env1 [env2 ...]
                      One or more environments defined inside of a tox.ini
                      file, listed in the order you want qtox to run them (put
                      fastest running tasks, like `pep8` / `flake8`, first for
                      best results).

Examples:

Creates a bash script to run three environments in one tox file:

    qtox -e pep8 py27 p36

Create a bash script to run six environments across two tox files:

    qtox -c acme-lib -e pep8 mypy pytest -c acme-rest-api -e pep8 mypy pytest

"""


class ParseMode(enum.Enum):
    C = "c"
    ENV = "e"
    NONE = None


def parse_cmds(args: t.List[str]) -> t.Optional[t.List[t.Tuple[t.Optional[str], str]]]:
    """Parses arguments, returns list of tox directory, environment pairs."""

    results: t.List[t.Tuple[t.Optional[str], str]] = []

    tox_dir: t.Optional[str] = None

    current_mode = ParseMode.NONE

    for index, arg in enumerate(args):
        if arg.startswith("-"):
            if arg == "-c":
                current_mode = ParseMode.C
                continue
            elif arg == "-e":
                current_mode = ParseMode.ENV
                continue
            else:
                print(f"Agument {index} was not expected: {arg}")
                print(USAGE)
                return None
        else:
            if current_mode == ParseMode.C:
                tox_dir = arg
            elif current_mode == ParseMode.ENV:
                results.append((tox_dir, arg))
            else:
                print("Error: expected `-c` or `-e`.")
                print(USAGE)
                return None

    if not results:
        print(USAGE)
        return None

    return results


def main() -> None:
    args = parse_cmds(sys.argv[1:])
    if not args:
        sys.exit(1)

    tox_inis: t.Dict[t.Optional[str], toxini.Ini] = {}

    def get_ini(c: t.Optional[str]) -> toxini.Ini:
        if c not in tox_inis:
            tox_inis[c] = toxini.get_ini(c)

        return tox_inis[c]

    envs: t.List[t.Tuple[str, toxini.Env]] = []
    for arg in args:
        tox_ini = get_ini(arg[0])
        env = tox_ini.get_env_info(arg[1])
        if arg[0]:
            name = f"{arg[0]} -> {arg[1]}"
        else:
            name = arg[1]
        envs.append((name, env))

    lines = bash.create_multi_tox_script(envs)

    print("\n".join(lines))

    # print(ini.toxinidir)
    # for env_name in args.envs:
    #     env = ini.get_env_info(env_name)
    #     print(f"[{env_name}]")

    #     # print(json.dumps(env, indent=4))
    #     # commands = json.loads(env["commands"])

    #     lines = bash.generate_tox_func(env)
    #     for l in lines:
    #         print(l)

    #     # print(env.envdir)
    #     # print(env.changedir)
