import configparser
import subprocess
import typing as t


def _run_tox_showconfig(tox_dir: t.Optional[str]) -> str:
    cmd = ["tox"]
    if tox_dir:
        cmd.extend(["-c", tox_dir])

    cmd.extend(["--showconfig"])
    output = subprocess.check_output(cmd)
    return output


class Ini:
    def __init__(self, content: str) -> None:
        self._config = configparser.ConfigParser()
        self._config.read_string(content)

    @property
    def toxinidir(self) -> str:
        return self._config.get(section="", option="toxinidir")


def get_ini(tox_dir: t.Optional[str]) -> Ini:
    content = _run_tox_showconfig(tox_dir)
    return Ini(content)
