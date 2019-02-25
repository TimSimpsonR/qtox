import configparser
import pathlib
import subprocess
import typing as t


Env = t.NewType("Env", dict)


def _run_tox_showconfig(
    root_directory: pathlib.Path, tox_dir: t.Optional[pathlib.Path]
) -> str:
    cmd = ["tox"]
    if tox_dir:
        cmd.extend(["-c", str(tox_dir)])

    cmd.extend(["--showconfig"])
    output = subprocess.check_output(cmd, cwd=root_directory)
    return output.decode("utf-8")


class Ini:
    def __init__(self, content: str) -> None:
        self._config = configparser.RawConfigParser()
        self._config.read_string(content)

    def get_env_info(self, name: str) -> Env:
        result = {k: v for k, v in self._config.items("_top_")}
        for section in [name, f"testenv:{name}"]:
            try:
                items = self._config.items(section)
            except configparser.NoSectionError:
                continue

            for k, v in items:
                result[k] = v

            return Env(result)

        raise ValueError(f"Could not find tox env {name}")

    @property
    def toxinidir(self) -> str:
        return self._config.get(section="_top_", option="toxinidir")


def get_ini(root_directory: pathlib.Path, tox_dir: t.Optional[pathlib.Path]) -> Ini:
    content = _run_tox_showconfig(root_directory, tox_dir)
    # Add section headers so the INI parser will work
    fake_content = f"[_top_]\n{content}"
    return Ini(fake_content)
