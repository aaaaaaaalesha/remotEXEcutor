from typing import TypeAlias, NamedTuple

Command: TypeAlias = str


class Scenario(NamedTuple):
    name: str
    commands: list[Command]
