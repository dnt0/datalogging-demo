from PySide6.QtCore import QObject, QRunnable, Slot, Signal
import serial
import time

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.runFlag = True

    @Slot()
    def run(self):
        while(self.runFlag):
            time.sleep(0.5)
            print("hello")

    def stop(self):
        self.runFlag = False
