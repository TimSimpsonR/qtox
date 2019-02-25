import enum
import os
import pathlib
import sys
import typing as t

from . import bash
from . import options
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
    ROOT = "r"
    NONE = None


def parse_cmds(args: t.List[str]) -> t.Optional[options.Options]:
    """Parses arguments, returns list of tox directory, environment pairs."""
    root_directory: t.Optional[pathlib.Path] = None
    envs: t.List[options.ToxEnv] = []

    tox_dir: t.Optional[pathlib.Path] = None

    current_mode = ParseMode.NONE

    for index, arg in enumerate(args):
        if arg.startswith("-"):
            if arg == "-c":
                current_mode = ParseMode.C
                continue
            elif arg == "-e":
                current_mode = ParseMode.ENV
                continue
            elif arg == "-r":
                current_mode = ParseMode.ROOT
                continue
            else:
                print(f"Agument {index} was not expected: {arg}")
                print(USAGE)
                return None
        else:
            if current_mode == ParseMode.C:
                tox_dir = pathlib.Path(arg)
            elif current_mode == ParseMode.ENV:
                envs.append(options.ToxEnv(tox_dir, arg))
            elif current_mode == ParseMode.ROOT:
                root_directory = pathlib.Path(arg)
            else:
                print("Error: expected `-c` or `-e`.")
                print(USAGE)
                return None

    if not envs:
        print(USAGE)
        return None

    if root_directory is None:
        root_directory = pathlib.Path.cwd()

    root_directory = root_directory.resolve()

    # Change all paths to be relative to the desired root directory
    # In their infinite wisdom, the Python gods haven't put an equivalent of
    # "relpath" into the new pathlib. (??)
    new_envs = [
        options.ToxEnv(
            pathlib.Path(os.path.relpath(str(env.tox_dir), str(root_directory))),
            env.env,
        )
        for env in envs
    ]
    return options.Options(root_directory, new_envs)


def main() -> None:
    options = parse_cmds(sys.argv[1:])
    if not options:
        sys.exit(1)

    tox_inis: t.Dict[t.Optional[str], toxini.Ini] = {}

    def get_ini(c: t.Optional[pathlib.Path]) -> toxini.Ini:
        assert options
        key = str(c) if c else None
        if c not in tox_inis:
            tox_inis[key] = toxini.get_ini(options.root, c)

        return tox_inis[key]

    envs: t.List[t.Tuple[str, toxini.Env]] = []
    for op_env in options.envs:
        tox_ini = get_ini(op_env.tox_dir)
        env = tox_ini.get_env_info(op_env.env)
        if op_env.tox_dir:
            name = f"{op_env.tox_dir} -> {op_env.env}"
        else:
            name = op_env.env
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
