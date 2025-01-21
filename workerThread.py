from PySide6.QtCore import QObject, QRunnable, Slot, Signal
import serial
import time
import pandas as pd
import os
from datetime import datetime, timedelta


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.runFlag = True
        self.enableUpdatesFlag = False

        self.ser = serial.Serial()
        self.ser.port = "COM3"
        self.ser.baudrate = 115200
        self.ser.timeout = 5

        self.dataLength = 6

    @Slot()
    def run(self):
        while(self.runFlag):
            if self.enableUpdatesFlag:
                self.update_data()

    def stop(self):
        self.runFlag = False

    def update_data(self):
        if self.ser.in_waiting:
            incomingData = self.ser.readline()
            incomingData = incomingData.decode('utf-8')
            dataRow = incomingData.removesuffix('\r\n').split(',')

            if len(dataRow) == self.dataLength:
                dataRow = [float(i) for i in dataRow]
                self.signals.result.emit(dataRow)

    def serial_connect(self):
        if (self.ser.is_open != True):
            self.ser.open()
            self.ser.reset_input_buffer()
            self.enableUpdatesFlag = True

    def serial_disconnect(self):
        self.enableUpdatesFlag = False
        self.ser.close()

    def serial_start(self):
        self.ser.write(b'start\n')

    def serial_end(self):
        self.ser.write(b'stop\n') 


class FileWorker(QRunnable):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.dataEntry = self.args[0]
        self.dataColumnNames = [
            "runtime [ms]",
            "sin1",
            "sin2",
            "sin2",
            "sin2",
            "sin2",
        ]

    @Slot()
    def run(self):
        dataFrame = pd.DataFrame(self.dataEntry)

        directory = "data"
        filename = ""

        if not os.path.exists(directory):
            os.makedirs(directory)

        latestFile = self.get_latest_file(directory)

        if latestFile:
            latestFileDirectory = os.path.join(directory, latestFile)
            latestFileTime = datetime.fromtimestamp(os.path.getctime(latestFileDirectory))
            timeDiff = datetime.now() - latestFileTime

            if timeDiff > timedelta(minutes=1):
                filename = datetime.now().replace(microsecond=0).isoformat().replace(':', '.')
            else:
                filename = latestFile[1:-5]

        else:
            filename = datetime.now().replace(microsecond=0).isoformat().replace(':', '.')
        
        fileDirectory = os.path.join(directory, '['+filename+'].csv')

        dataFrame.to_csv(fileDirectory, mode='a', header=self.dataColumnNames, index=False)

        self.signals.finished.emit()

    def get_latest_file(self, directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        if not files:
            return None
        
        # Get the file with the latest creation time
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
        return latest_file