import ast
import pathlib
import shlex
import typing as t

from . import toxini


def generate_tox_func(env: toxini.Env) -> t.List[str]:
    """Given a tox env dictionary, returns bash code to run."""
    envdir = pathlib.Path(env["envdir"])
    if not envdir.exists():
        raise RuntimeError(
            f"Can't generate env: path {envdir} does not exist."
            "Make sure tox has been run once to set up all virtualenvs and try "
            "again."
        )

    bindir = envdir / "bin"
    whitelist_externals: t.List[str] = ast.literal_eval(env["whitelist_externals"])
    commands: t.List[t.List[str]] = ast.literal_eval(env["commands"])
    changedir: t.Optional[pathlib.Path] = None if not env[
        "changedir"
    ] else pathlib.Path(env["changedir"])

    lines: t.List[str] = []

    if changedir:
        lines.append(f"pushd {changedir}")

    for command in commands:
        if "setenv" in env and env["setenv"].startswith("SetenvDict: "):
            sed = ast.literal_eval(env["setenv"][12:])
            for k, v in sed.items():
                v = v.format(**env)
                lines.append(shlex.quote(k) + "='" + shlex.quote(v) + "' \\")

        bin_command = bindir / command[0]
        if not bin_command.exists():
            if command[0] not in whitelist_externals:
                raise RuntimeError(
                    f"Error generating command: {command}\n"
                    f"{command[0]} not in virtualenv or whitelist_externals."
                )
            command_0 = shlex.quote(command[0])
        else:
            command_0 = shlex.quote(str(bin_command))

        command_line = [command_0] + [shlex.quote(s) for s in command[1:]]
        lines.append(" ".join(command_line))
        lines.append("")

    if changedir:
        lines.append("popd")

    return lines


def create_bash_script(ini: toxini.Ini, envs: t.List[str]) -> t.List[str]:
    lines: t.List[str] = []
    lines += ["set -euo pipefail", "", "readonly tmpdir='/tmp'", ""]

    for index, env_name in enumerate(envs):
        env = ini.get_env_info(env_name)
        lines.append(f"function run_env_{index}(){{")
        lines.append("    echo '" + ("-" * 52) + "'")
        lines.append(f"    echo '| {env_name:<48} |'")
        lines.append("    echo '" + ("-" * 52) + "'")
        func_lines = generate_tox_func(env)
        for l in func_lines:
            lines.append("    " + l)
        lines.append("}")
        lines.append("")

    lines.append("")

    for index, _env_name in enumerate(envs):
        lines.append(f'run_env_{index} &> "${{tmpdir}}"/{index} &')
        lines.append(f"pids[{index}]=$!")
        lines.append("")

    lines.append("")

    lines += [
        "status=0",
        "index=0",
        "set +e",
        "for pid in ${pids[*]}; do",
        "    if [ $status -eq 0 ]; then",
        '        tail -f -n +1 --pid=$pid "${tmpdir}/${index}" &',
        "        tail_pid=$!",
        "        wait $pid",
        "        status=$?",
        "        wait $tail_pid",
        "    else",
        '        kill "${pid}" &> /dev/null',
        "    fi",
        "    index=$(($index + 1))",
        "done",
        "",
        "if [ $status -eq 0 ]; then",
        "    echo '                                    O K   : )'",
        "else",
        "    echo '                          F A I L E D !   :('",
        "fi",
        "",
        "exit $status",
    ]
    return lines
