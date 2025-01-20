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

        self.worker = workerThread.Worker()
        self.threadpool.start(self.worker)

        self.pushButton_4.clicked.connect(self.worker.serial_connect)
        self.pushButton_5.clicked.connect(self.worker.serial_disconnect)
        self.pushButton.clicked.connect(self.worker.serial_start)
        self.pushButton_2.clicked.connect(self.worker.serial_end)

    def plot(self, hour, temperature):
        self.graphWidget.plot(hour, temperature)

    def closeEvent(self, event):
        # Override the close event to stop the worker when exiting the app
        if self.worker:
            self.worker.stop()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
