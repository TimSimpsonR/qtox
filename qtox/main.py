import argparse

from . import bash
from . import toxini


def main() -> None:
    parser = argparse.ArgumentParser("qtox")
    parser.add_argument(
        "-c", help="Directory containing tox.ini", type=str, default=None
    )
    parser.add_argument(
        "--envs",
        nargs="+",
        help="List of environments, in the order you want qtox to show them "
        "(defaults to using envlist specified at top of tox.ini file",
        required=True,
    )

    args = parser.parse_args()

    ini = toxini.get_ini(args.c)

    lines = bash.create_bash_script(ini, args.envs)

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
