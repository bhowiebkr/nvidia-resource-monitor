import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt, QTimer
from PySide2.QtCharts import QtCharts
from pynvml import *

nvmlInit()
handle = nvmlDeviceGetHandleByIndex(0)

FREQUENCY = 10
MAX_DATAPOINTS = 500

# Dark theme setup
palette = QPalette()
palette.setColor(QPalette.Window, QColor(27, 35, 38))
palette.setColor(QPalette.WindowText, QColor(234, 234, 234))
palette.setColor(QPalette.Base, QColor(27, 35, 38))
palette.setColor(QPalette.Disabled, QPalette.Base, QColor(27 + 5, 35 + 5, 38 + 5))
palette.setColor(QPalette.AlternateBase, QColor(12, 15, 16))
palette.setColor(QPalette.ToolTipBase, QColor(27, 35, 38))
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, QColor(200, 200, 200))
palette.setColor(QPalette.Disabled, QPalette.Text, QColor(100, 100, 100))
palette.setColor(QPalette.Button, QColor(27, 35, 38))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, QColor(100, 215, 222))
palette.setColor(QPalette.Link, QColor(126, 71, 130))
palette.setColor(QPalette.Highlight, QColor(126, 71, 130))
palette.setColor(QPalette.HighlightedText, Qt.white)
palette.setColor(QPalette.Disabled, QPalette.Light, Qt.black)
palette.setColor(QPalette.Disabled, QPalette.Shadow, QColor(12, 15, 16))


class NvidiaResources(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Nvidia Resources")

        settings = QtCore.QSettings("nvidia-resources", "NvidiaResources")

        try:
            self.restoreGeometry(settings.value("geometry"))
        except AttributeError:
            logging.warning("Unable to load settings. First time opening the tool?")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Time)
        self.timer.start(FREQUENCY)
        self.index = MAX_DATAPOINTS

        self.chart = QtCharts.QChart()
        self.chart.setTheme(QtCharts.QChart.ChartThemeDark)
        self.series = QtCharts.QLineSeries(self)
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.series)

        self.value_axis = QtCharts.QValueAxis()
        self.value_axis.setTickCount(5)
        mem_total = nvmlDeviceGetMemoryInfo(handle).total / 1024 / 1024
        self.value_axis.setMax(mem_total)
        self.chart.addAxis(self.value_axis, Qt.AlignLeft)

        for i in range(MAX_DATAPOINTS):
            self.series.append(i, 0)

        # Creating QChartView
        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.chart_view)

        self.setLayout(self.main_layout)

    def Time(self):
        memInfo = nvmlDeviceGetMemoryInfo(handle)
        used = memInfo.used / 1048576
        self.chart.setTitle(f"{used} MB")  # 1024 / 1024
        self.series.append(self.index, used)
        if self.index > MAX_DATAPOINTS:
            self.series.remove(0)

        self.index += 1

        # I don't like this. must be a better way.
        self.chart.removeSeries(self.series)
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.value_axis)

    def closeEvent(self, event):
        self.settings = QtCore.QSettings("nvidia-resources", "NvidiaResources")
        self.settings.setValue("geometry", self.saveGeometry())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(palette)
    widget = NvidiaResources()
    widget.show()
    sys.exit(app.exec_())
