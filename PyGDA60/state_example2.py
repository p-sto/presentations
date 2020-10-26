from enum import Enum
from typing import Optional, List


class ProcStateStatus(Enum):
    """Lista stanow w jakich moze znajdowac sie subproces, moze byc to tez po prostu lista eventow,
    ktore wplywaja na finalny status master procesu"""

    NEW = 'new'
    RUNNING = 'running'
    DONE = 'done'
    ERROR = 'error'
    TIMEOUT = 'timeout'


class MasterProcStateStatus(Enum):
    """Lista stanow w jakich moze znajdowac sie master proces"""

    RUNNING = 'running'
    DONE = 'done'
    ERROR = 'error'
    TIMEOUT = 'timeout'


class MasterProcessStateInterface:
    """
    Definiujemy interfejs, ktory bedzie dostarczac metody odpowiedzialne za implementacje
    logiki biznesowej dla poszczegolnych pobudzen/stanow

    -> kazda metoda odpowiada akcji dla kazdego ze stanow z ProcState z poprzedniego przykladu
    """

    state_status: MasterProcStateStatus

    def on_new(self):
        raise NotImplementedError()

    def on_running(self):
        raise NotImplementedError()

    def on_done(self):
        raise NotImplementedError()

    def on_error(self):
        raise NotImplementedError()

    def on_timeout(self):
        raise NotImplementedError()


class RunningMasterProcessState(MasterProcessStateInterface):
    """Ilosc implementacji odpowiada ilości stanow, w ktorych moze znajdowac sie master process"""

    state_status = MasterProcStateStatus.RUNNING

    def on_new(self):
        return self

    def on_running(self):
        return self

    def on_done(self):
        return self

    def on_error(self):
        return ErrorMasterProcessState()

    def on_timeout(self):
        return TimeoutMasterProcessState()


class DoneMasterProcessState(MasterProcessStateInterface):

    state_status = MasterProcStateStatus.DONE

    def on_new(self):
        return RunningMasterProcessState()

    def on_running(self):
        return RunningMasterProcessState()

    def on_done(self):
        return self

    def on_error(self):
        return ErrorMasterProcessState()

    def on_timeout(self):
        return TimeoutMasterProcessState()


class ErrorMasterProcessState(MasterProcessStateInterface):

    state_status = MasterProcStateStatus.ERROR

    def on_new(self):
        return self

    def on_running(self):
        return self

    def on_done(self):
        return self

    def on_error(self):
        return self

    def on_timeout(self):
        return self


class TimeoutMasterProcessState(MasterProcessStateInterface):

    state_status = MasterProcStateStatus.TIMEOUT

    def on_new(self):
        return self

    def on_running(self):
        return self

    def on_done(self):
        return self

    def on_error(self):
        return ErrorMasterProcessState()

    def on_timeout(self):
        return self


class SubProcess:

    def __init__(self, state: ProcStateStatus = ProcStateStatus.NEW):
        self.state = state

    def do(self):
        """Jakas logika biznesowa odpowiedzialna za stan danego procesu"""


class MasterProc:
    """Proces, ktorego stan bedzie zalezec od statusow subprocesow"""

    def __init__(self, subprocesses: Optional[List[SubProcess]] = None):
        self.state = DoneMasterProcessState()
        self.subprocesses = subprocesses

    @staticmethod
    def _get_status_based_on_subproc(subprc_status: ProcStateStatus,
                                     curr_state: MasterProcessStateInterface
                                     ) -> MasterProcessStateInterface:
        mapping = {
            ProcStateStatus.NEW: curr_state.on_new(),
            ProcStateStatus.RUNNING: curr_state.on_running(),
            ProcStateStatus.DONE: curr_state.on_done(),
            ProcStateStatus.ERROR: curr_state.on_error(),
            ProcStateStatus.TIMEOUT: curr_state.on_timeout()
        }
        return mapping.get(subprc_status)

    def get_current_state(self) -> MasterProcStateStatus:
        for proc in self.subprocesses:
            self.state = self._get_status_based_on_subproc(proc.state, self.state)
        return self.state.state_status


if __name__ == '__main__':

    sub_proc1 = SubProcess(state=ProcStateStatus.DONE)
    sub_proc2 = SubProcess(state=ProcStateStatus.DONE)
    sub_proc3 = SubProcess(state=ProcStateStatus.DONE)

    master_proc = MasterProc([sub_proc1, sub_proc2, sub_proc3])
    print(master_proc.get_current_state())
