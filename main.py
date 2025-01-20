import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThreadPool
import pyqtgraph as pg
import serial
import time
import workerThread

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.plot(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], # Hours
            [30, 32, 34, 32, 33, 31, 29, 32, 35, 45], # Temperature
        )

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        #self.timer.timeout.connect(self.update_data)

        self.threadpool = QThreadPool()

        self.worker = workerThread.Worker(self.update_data)
        self.threadpool.start(self.worker)
        active_threads = self.threadpool.activeThreadCount()
        thread_count = self.threadpool.maxThreadCount()
        print(active_threads)

        self.pushButton.clicked.connect(self.worker.serial_start)
        self.pushButton_2.clicked.connect(self.worker.serial_end)


    def plot(self, hour, temperature):
        self.graphWidget.plot(hour, temperature)

    def start(self):
        if (self.ser.is_open != True):
            self.ser.open()
            self.ser.reset_input_buffer()

        time.sleep(2)
        self.ser.write(b'start\n')
        self.timer.start()

    def stop(self):
        #self.timer.stop()
        time.sleep(0.5)

    def update_data(self):
        if self.ser.in_waiting:
            incomingData = self.ser.readline()
            incomingData = incomingData.decode('utf-8')
            dataRow = incomingData.removesuffix('\r\n').split(',')

            if len(dataRow) == self.dataLength:
                print(dataRow)


    def closeEvent(self, event):
        # Override the close event to stop the worker when exiting the app
        if self.worker:
            self.worker.stop()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
