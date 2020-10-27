from enum import Enum
from typing import Optional, List

from statemachine import StateMachine, State


class MasterProcessState(StateMachine):
    DONE = State('done', initial=True)
    RUNNING = State('running')
    ERROR = State('error')
    TIMEOUT = State('timeout')

    new = RUNNING.to(RUNNING) | DONE.to(RUNNING) | ERROR.to(ERROR) | TIMEOUT.to(TIMEOUT)
    running = RUNNING.to(RUNNING) | DONE.to(RUNNING) | ERROR.to(ERROR) | TIMEOUT.to(TIMEOUT)
    done = RUNNING.to(RUNNING) | DONE.to(DONE) | ERROR.to(ERROR) | TIMEOUT.to(TIMEOUT)
    error = RUNNING.to(ERROR) | DONE.to(ERROR) | ERROR.to(ERROR) | TIMEOUT.to(ERROR)
    timeout = RUNNING.to(TIMEOUT) | DONE.to(TIMEOUT) | ERROR.to(ERROR) | TIMEOUT.to(TIMEOUT)


class ProcStateStatus(Enum):
    """Lista stanow w jakich moze znajdowac sie subproces, moze byc to tez po prostu lista eventow,
    ktore wplywaja na finalny status master procesu"""

    NEW = 'new'
    RUNNING = 'running'
    DONE = 'done'
    ERROR = 'error'
    TIMEOUT = 'timeout'


class SubProcess:

    def __init__(self, state: ProcStateStatus = ProcStateStatus.NEW):
        self.state = state

    def do(self):
        """Jakas logika biznesowa odpowiedzialna za stan danego procesu"""


class MasterProc:
    """Proces, ktorego stan bedzie zalezec od statusow subprocesow"""

    def __init__(self, subprocesses: Optional[List[SubProcess]] = None):
        self.subprocesses = subprocesses
        self.state_machine = MasterProcessState()

    @staticmethod
    def _get_status_based_on_subproc(subprc_status: ProcStateStatus,
                                     curr_state: MasterProcessState
                                     ) -> None:

        mapping = {
            ProcStateStatus.NEW: getattr(curr_state, 'new'),
            ProcStateStatus.RUNNING: getattr(curr_state, 'running'),
            ProcStateStatus.DONE: getattr(curr_state, 'done'),
            ProcStateStatus.ERROR: getattr(curr_state, 'error'),
            ProcStateStatus.TIMEOUT: getattr(curr_state, 'timeout')
        }
        method = mapping.get(subprc_status)
        method()

    def get_current_state(self) -> State:
        if not self.subprocesses:
            return MasterProcessState.ERROR     # maly hax na init state'a
        for proc in self.subprocesses:
            self._get_status_based_on_subproc(proc.state, self.state_machine)
        return self.state_machine.current_state


if __name__ == '__main__':

    sub_proc1 = SubProcess(state=ProcStateStatus.TIMEOUT)
    sub_proc2 = SubProcess(state=ProcStateStatus.DONE)
    sub_proc3 = SubProcess(state=ProcStateStatus.DONE)

    master_proc = MasterProc([sub_proc1, sub_proc2, sub_proc3])
    print(master_proc.get_current_state())
