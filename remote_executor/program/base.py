import os
from pathlib import Path

import yaml

from remote_executor.program.types import Command, Scenario
from remote_executor.settings import (
    CONFIG_ENCODING,
    LOCAL_CONFIG_NAME,
    PROGRAM_KEY,
    DESCRIPTION_KEY,
    PRE_EXEC_KEY,
    BODY_KEY,
    POST_EXEC_KEY,
)


class BadConfigError(Exception):
    pass


class Program:
    REQUIRED_KEYS = (PROGRAM_KEY, BODY_KEY)
    COMMAND_KEYS = (PRE_EXEC_KEY, BODY_KEY, POST_EXEC_KEY)

    def __init__(self, config_data: dict[str, str], name: str, program_dir: Path):
        for key in self.REQUIRED_KEYS:
            if key not in config_data:
                raise BadConfigError(f'{key} not found in config parameters for {name}')

        self.name: str = name
        self.program_dir: Path = program_dir

        description: str | None = config_data.get(DESCRIPTION_KEY)
        self.description: str = description if description is not None else ''
        self.program: str | None = config_data.get(PROGRAM_KEY)

        self.pre_exec_commands: list[Command] = self.__prepare_commands(
            commands=config_data.get(PRE_EXEC_KEY),
        )
        self.post_exec_commands: list[Command] = self.__prepare_commands(
            commands=config_data.get(POST_EXEC_KEY),
        )

        body_scenarios: dict[str, str] = config_data.get(BODY_KEY)
        self.body_scenarios: list[Scenario] = self.__prepare_scenarios(body_scenarios)

        self.scenarios_on_execute: list[Scenario] = []

    def __str__(self):
        return f'{self.name}: {self.scenarios_on_execute}'

    def setup_execute_scenarios(self, scenarios_indexes: list[int]) -> None:
        self.scenarios_on_execute = [
            self.body_scenarios[index]
            for index in scenarios_indexes
        ]

    @staticmethod
    def __prepare_commands(commands: str | None) -> list[Command]:
        if commands is None:
            return []

        return commands.strip('\r\n ').split('\n')

    @staticmethod
    def __prepare_scenarios(scenarios: dict[str, str]) -> list[Scenario]:
        return [
            Scenario(
                name=name,
                commands=commands.strip('\r\n ').split('\n'),
            )
            for name, commands in scenarios.items()
        ]


def scan_programs(programs_dir: Path) -> list[Program]:
    programs = []
    for root, _, files in os.walk(programs_dir):
        if LOCAL_CONFIG_NAME in set(files):
            root_dir = Path(root)
            fetch_programs(programs, root_dir)

    return programs


def fetch_programs(programs: list[Program], root_dir: Path) -> None:
    config_path = root_dir / LOCAL_CONFIG_NAME
    config_text = config_path.read_text(encoding=CONFIG_ENCODING)
    config_data = yaml.safe_load(config_text)
    for name, configuration in config_data.items():
        programs.append(Program(configuration, name=name, program_dir=root_dir))
