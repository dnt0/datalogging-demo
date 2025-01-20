from PySide6.QtCore import QObject, QRunnable, Slot, Signal
import serial
import time

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
        self.ser.port = "/dev/ttyACM0"
        self.ser.baudrate = 115200
        self.ser.timeout = 5

        self.dataLength = 6

    @Slot()
    def run(self):
        while(self.runFlag):
            if self.enableUpdatesFlag:
                self.update_data()
            #time.sleep(0.5)

    def stop(self):
        self.runFlag = False

    def update_data(self):
        if self.ser.in_waiting:
            incomingData = self.ser.readline()
            incomingData = incomingData.decode('utf-8')
            dataRow = incomingData.removesuffix('\r\n').split(',')

            if len(dataRow) == self.dataLength:
                print(dataRow)

    def serial_start(self):
        if (self.ser.is_open != True):
            self.ser.open()
            self.ser.reset_input_buffer()
            self.enableUpdatesFlag = True

        time.sleep(0.5)
        self.ser.write(b'start\n')

    def serial_end(self):
        self.ser.write(b'stop\n') 
