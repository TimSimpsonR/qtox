import configparser
import pathlib
import subprocess
import typing as t


def _run_tox_showconfig(
    root_directory: pathlib.Path, tox_dir: t.Optional[pathlib.Path]
) -> str:
    cmd = ["tox"]
    if tox_dir:
        cmd.extend(["-c", str(tox_dir)])

    cmd.extend(["--showconfig"])
    output = subprocess.check_output(cmd, cwd=root_directory)
    return output.decode("utf-8")


class Env:
    def __init__(
        self, cwd: pathlib.Path, tox_dir: t.Optional[pathlib.Path], settings: dict
    ) -> None:
        self._cwd = cwd
        self.tox_dir = tox_dir
        self.settings = settings

    @property
    def cwd(self) -> str:
        if 'changedir' in self.settings:
            return self.settings['changedir']
        else:
            return self._cwd

class Ini:
    def __init__(
        self, cwd: pathlib.Path, tox_dir: t.Optional[pathlib.Path], content: str
    ) -> None:
        self._config = configparser.RawConfigParser()
        self._config.read_string(content)
        self._cwd = cwd
        self._tox_dir = tox_dir

    def get_env_info(self, name: str) -> Env:
        result = {k: v for k, v in self._config.items("_top_")}
        if self._tox_dir:
            result['toxinidir'] = self._tox_dir.absolute()
        for section in [name, f"testenv:{name}"]:
            try:
                items = self._config.items(section)
            except configparser.NoSectionError:
                continue

            for k, v in items:
                result[k] = v

            return Env(self._cwd, self._tox_dir, result)

        raise ValueError(f"Could not find tox env {name}")

    @property
    def toxinidir(self) -> str:
        return self._config.get(section="_top_", option="toxinidir")


def get_ini(cwd: pathlib.Path, tox_dir: t.Optional[pathlib.Path]) -> Ini:
    content = _run_tox_showconfig(cwd, tox_dir)
    # Add section headers so the INI parser will work
    fake_content = f"[_top_]\n{content}"
    return Ini(cwd, tox_dir, fake_content)
