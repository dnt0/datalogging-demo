import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThreadPool
import pyqtgraph as pg
import serial
import time
import workerThread
from collections import deque
from random import randint
from datetime import datetime, timedelta


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

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.save_data)
        self.timer.start()

        self.threadpool = QThreadPool()

        self.worker = workerThread.Worker()
        self.threadpool.start(self.worker)
        self.worker.signals.result.connect(self.plot_graph)

        self.fileEntry = []

        self.pushButton_4.clicked.connect(self.worker.serial_connect)
        self.pushButton_5.clicked.connect(self.worker.serial_disconnect)
        self.pushButton.clicked.connect(self.startSequence)
        self.pushButton_2.clicked.connect(self.worker.serial_end)
        self.pushButton_3.clicked.connect(self.worker.serial_clear_faults)

        self.previousTime = datetime.fromtimestamp(0)

    def closeEvent(self, event):
        # Override the close event to stop the worker when exiting the app
        if self.worker:
            self.worker.stop()
        event.accept()

    def startSequence(self):
        modeSelect = self.comboBoxModeSelect.currentText()
        self.clear_plot_data()
        self.worker.serial_start(modeSelect)

    def plot_graph(self, workerResult):
        self.fileEntry.append(workerResult)

        currentTime = datetime.now()
        timeInterval = currentTime - self.previousTime
        if timeInterval > timedelta(milliseconds=500):                              # Update texts every 500ms
            self.update_texts(workerResult)
            self.previousTime = currentTime

        self.plotData["channel1"]["x"].append(workerResult[0])
        self.plotData["channel1"]["y"].append(workerResult[1])
        
        self.plotData["channel2"]["x"].append(workerResult[0])
        self.plotData["channel2"]["y"].append(workerResult[2])

        self.dataLine1.setData(list(self.plotData["channel1"]["x"]), list(self.plotData["channel1"]["y"]))
        self.dataLine2.setData(list(self.plotData["channel2"]["x"]), list(self.plotData["channel2"]["y"]))

    def clear_plot_data(self):
        for channel in self.plotData.values():
            for dataQueue in channel.values():
                dataQueue.clear()
    
    def save_data(self):
        if len(self.fileEntry):
            fileEntryCopy = self.fileEntry.copy()
            self.clear_file_entry()

            self.worker2 = workerThread.FileWorker(fileEntryCopy)
            # self.worker2.signals.finished.connect(self.clear_file_entry)
            self.threadpool.start(self.worker2)
    
    def clear_file_entry(self):
        self.fileEntry.clear()

    def update_texts(self, workerResult):
        formattedRuntime = self.format_elapsed_time(workerResult[0])

        self.labelCycle.setText("%d" % workerResult[0])
        self.labelRuntime.setText(formattedRuntime)
        self.labelPosition.setText("%.2f" % workerResult[1])
        self.labelTemperature1.setText("%.2f" % workerResult[2])
        self.labelTemperature2.setText("%.2f" % workerResult[3])
        self.labelTemperature3.setText("%.2f" % workerResult[4])

        self.labelOpenCommand.setText("%.2f" % workerResult[5])
        self.labelCloseCommand.setText("%.2f" % workerResult[5])
        self.labelDoorOpened.setText("%.2f" % workerResult[5])
        self.labelDoorClosed.setText("%.2f" % workerResult[5])

        self.labelHomePosition.setText("%.2f" % workerResult[5])
        self.labelFault.setText("%.2f" % workerResult[5])

    def format_elapsed_time(self, milliseconds):
        totalSeconds = milliseconds // 1000

        days = totalSeconds // (24*3600)
        totalSeconds %= 24 * 3600

        hours = totalSeconds // 3600
        totalSeconds %= 3600

        minutes = totalSeconds // 60
        seconds = totalSeconds % 60

        return "%d day, %d hr, %d min, %d sec " % (days, hours, minutes, seconds)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()