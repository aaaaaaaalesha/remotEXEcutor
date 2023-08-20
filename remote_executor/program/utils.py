from pathlib import Path

from remote_executor.cli.questions import (
    ask_programs,
    ask_scenarios,
    ask_are_you_sure,
)
from remote_executor.program.base import scan_programs, Program
from remote_executor.log import logger
from remote_executor.settings import (
    LOCAL_CONFIG_NAME,
    PROGRAMS_DIR,
)


def choose_program_scenarios(programs_dir: Path) -> list[Program]:
    programs: list[Program] = scan_programs(programs_dir)
    if not programs:
        logger.error(
            'You have no choices for remote execution. '
            f'Please, add {LOCAL_CONFIG_NAME} near executable in {PROGRAMS_DIR}.'
        )
        exit(1)

    ready_programs: list[Program] = []
    is_scenarios_selected = False
    while not is_scenarios_selected:
        ready_programs.clear()
        chosen_programs: list[Program] = ask_programs(programs)
        if not chosen_programs:
            logger.info('You have choose nothing. Ok, goodbye...')
            exit(0)

        for program in chosen_programs:
            if len(program.body_scenarios) == 1:
                logger.info(f'{program.name} have only one scenario: {program.body_scenarios[0]}')
                scenarios_indexes = [0]
            else:
                scenarios_indexes: list[int] = ask_scenarios(program)

            program.setup_execute_scenarios(scenarios_indexes)
            ready_programs.append(program)

        logger.info('Selected following programs and scenarios:')
        logger.info('\n'.join([
            str(program)
            for program in ready_programs
        ]))
        is_scenarios_selected = ask_are_you_sure()

    return ready_programs
