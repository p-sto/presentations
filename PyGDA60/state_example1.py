from enum import Enum
from typing import List, Optional


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


class SubProcess:

    def __init__(self, state: ProcStateStatus = ProcStateStatus.NEW):
        self.state = state

    def do(self):
        """Jakas logika biznesowa odpowiedzialna za stan danego procesu"""


class MasterProc:
    """Proces, ktorego stan bedzie zalezec od statusow subprocesow"""

    def __init__(self, subprocesses: Optional[List[SubProcess]] = None):
        self.state = MasterProcStateStatus.RUNNING      # stan poczatkowy
        self.subprocesses = subprocesses

    def get_current_state(self) -> MasterProcStateStatus:
        """Obecny stan zalezy od stanow procesow zaleznych"""
        if not self.subprocesses:
            # jesli nie ma subprocesow, to zalozmy ze finalny stan jest DONE
            return MasterProcStateStatus.DONE
        if ProcStateStatus.ERROR in [proc.state for proc in self.subprocesses]:
            # jesli przynajmniej jeden subproces ma status ERROR, to caly master process tez
            return MasterProcStateStatus.ERROR
        if ProcStateStatus.TIMEOUT in [proc.state for proc in self.subprocesses]:
            # jesli ktorys z subprocesow ma status TIMEOUT, to finalny stan jest TIMEOUT
            return MasterProcStateStatus.TIMEOUT
        if all([proc.state == ProcStateStatus.DONE for proc in self.subprocesses]):
            # jesli wszystkie subprocesy sa w stanie DONE to master proces tez jest DONE
            return MasterProcStateStatus.DONE
        # w pozostalych sytuacjach subprocesy sa w stanie NEW albo RUNNING, wiec master proces tez sie w RUNNING
        return MasterProcStateStatus.RUNNING


if __name__ == '__main__':

    ugotowac_miesko = SubProcess(state=ProcStateStatus.DONE)
    przygotowac_salatke = SubProcess(state=ProcStateStatus.DONE)
    upiec_frytki = SubProcess(state=ProcStateStatus.DONE)

    obiad = MasterProc([ugotowac_miesko, przygotowac_salatke, upiec_frytki])
    print(obiad.get_current_state())
