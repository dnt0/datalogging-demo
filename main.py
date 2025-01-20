import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThreadPool
import pyqtgraph as pg
import serial
import time
import workerThread
from collections import deque
from random import randint

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.numberOfSamples = 1000
        self.plotData = {
                "channel1": {"x": deque(maxlen=self.numberOfSamples), "y": deque(maxlen=self.numberOfSamples)}, 
                "channel2": {"x": deque(maxlen=self.numberOfSamples), "y": deque(maxlen=self.numberOfSamples)}, 
                }

        self.graphWidget.setBackground('w')
        self.graphWidget.setYRange(-105, 105)
        self.graphWidget.addLegend()
        

        self.dataLine1 = self.graphWidget.plot([], [], name="Sensor1", pen='b')
        self.dataLine2 = self.graphWidget.plot([], [], name="Sensor2", pen='r')

        #self.timer = QTimer(self)
        #self.timer.setInterval(1000)
        #self.timer.timeout.connect(self.update_data)

        self.threadpool = QThreadPool()

        self.worker = workerThread.Worker()
        self.threadpool.start(self.worker)
        self.worker.signals.result.connect(self.plot_graph)

        self.pushButton_4.clicked.connect(self.worker.serial_connect)
        self.pushButton_5.clicked.connect(self.worker.serial_disconnect)
        self.pushButton.clicked.connect(self.worker.serial_start)
        self.pushButton_2.clicked.connect(self.worker.serial_end)

    def closeEvent(self, event):
        # Override the close event to stop the worker when exiting the app
        if self.worker:
            self.worker.stop()
        event.accept()

    def plot_graph(self, workerResult):
        self.plotData["channel1"]["x"].append(workerResult[0])
        self.plotData["channel1"]["y"].append(workerResult[1])
        
        self.plotData["channel2"]["x"].append(workerResult[0])
        self.plotData["channel2"]["y"].append(workerResult[2])

        self.dataLine1.setData(list(self.plotData["channel1"]["x"]), list(self.plotData["channel1"]["y"]))
        self.dataLine2.setData(list(self.plotData["channel2"]["x"]), list(self.plotData["channel2"]["y"]))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
