import pathlib
import typing as t


ToxEnv = t.NamedTuple("ToxEnv", [("tox_dir", t.Optional[pathlib.Path]), ("env", str)])


class Options:
    def __init__(self, root: pathlib.Path, envs: t.List[ToxEnv]) -> None:
        self.root = root
        self.envs = envs
