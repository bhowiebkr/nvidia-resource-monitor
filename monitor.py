import sys
from PySide2 import QtCore, QtGui, QtWidgets, QtCharts
from PySide2.QtCharts import QtCharts
from pynvml import *

nvmlInit()
handle = nvmlDeviceGetHandleByIndex(0)

FREQUENCY = 10
MAX_DATAPOINTS = 500

# Dark theme setup
palette = QtGui.QPalette()
palette.setColor(QtGui.QPalette.Window, QtGui.QColor(27, 35, 38))
palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(234, 234, 234))
palette.setColor(QtGui.QPalette.Base, QtGui.QColor(27, 35, 38))
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(27 + 5, 35 + 5, 38 + 5))
palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(12, 15, 16))
palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(27, 35, 38))
palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
palette.setColor(QtGui.QPalette.Text, QtGui.QColor(200, 200, 200))
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(100, 100, 100))
palette.setColor(QtGui.QPalette.Button, QtGui.QColor(27, 35, 38))
palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(100, 215, 222))
palette.setColor(QtGui.QPalette.Link, QtGui.QColor(126, 71, 130))
palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(126, 71, 130))
palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtCore.Qt.black)
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, QtGui.QColor(12, 15, 16))


class NvidiaResources(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Nvidia Resources")

        settings = QtCore.QSettings("nvidia-resources", "NvidiaResources")

        try:
            self.restoreGeometry(settings.value("geometry"))
        except AttributeError:
            logging.warning("Unable to load settings. First time opening the tool?")

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Time)
        self.timer.start(FREQUENCY)
        self.index = MAX_DATAPOINTS

        self.chart = QtCharts.QChart()
        self.chart.setTheme(QtCharts.QChart.ChartThemeDark)
        self.series = QtCharts.QLineSeries(self)
        self.chart.legend().setVisible(False)

        self.value_axis = QtCharts.QValueAxis()
        self.value_axis.setTickCount(5)
        mem_total = nvmlDeviceGetMemoryInfo(handle).total / 1024 / 1024
        self.value_axis.setMax(mem_total)
        self.chart.addAxis(self.value_axis, QtCore.Qt.AlignLeft)

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
