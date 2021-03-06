# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtCore, QtChart
from PyQt5.QtCore import pyqtSignal

from liquidctl.common.preset import DeviceLightingPreset

# default explode distances
RING_HOVER = 0.065
RING_NORMAL = 0.035

_SLICE_BORDER = {
    'enable'  : QtGui.QColor(1,1,1,160),
    'disable' : QtGui.QColor(127,127,127,160),
    'picked'  : QtGui.QPalette().color(QtGui.QPalette.HighlightedText)
}


# QRingWidget - widget based on QtChart that provides a segmented ring
class QRingWidget(QtCore.QObject):

    slice_clicked = pyqtSignal(QtChart.QPieSlice)
    slice_hovered = pyqtSignal(QtChart.QPieSlice, bool)
    slice_dblclicked = pyqtSignal(QtChart.QPieSlice)

    def __init__(self, chartViewParent: QtChart.QChartView, *preset):
        super().__init__()

        self.__chart = QtChart.QChart()
        self.__chart.legend().hide()
        self.__chart.setMinimumHeight(180)
        self.__chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.__series = QtChart.QPieSeries()
        self.__series.setHoleSize(0.58)
        self.__series.setPieSize(0.75)

        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setExploded(True)
            ps.setExplodeDistanceFactor(RING_NORMAL)

            ps.clicked.connect(self.__slice_clicked)
            ps.hovered.connect(self.__slice_hovered)
            ps.doubleClicked.connect(self.__slice_dblclicked)

            self.__series.append(ps)

        self.__chart.addSeries(self.__series)

        chartViewParent.setRenderHint(QtGui.QPainter.Antialiasing, True)
        chartViewParent.setChart(self.__chart)

        self.__last_slice = self.__series.slices()[0]

    def __slice_clicked(self):
        self.slice_clicked.emit(self.sender())

    def __slice_hovered(self, state):
        ps = self.sender()

        self.slice_hovered.emit(ps, state)

        if state:
            self.last_color = ps.color()
            ps.setColor(self.last_color.lighter())
        else:
            ps.setColor(self.last_color)

        ps.setExplodeDistanceFactor(RING_HOVER if state else RING_NORMAL)


    def __slice_dblclicked(self):
        self.slice_dblclicked.emit(self.sender())

    def setBackgroundColor(self, color):
        brush = QtGui.QBrush(color)
        self.__chart.setBackgroundBrush(brush)

    def highlight_slices(self, maxcolors, pickedObject):

        for i, ps in enumerate(self.__series.slices()):
            ps.setBorderColor(_SLICE_BORDER['enable'])

        for i, ps in enumerate(self.__series.slices()):
            if i == maxcolors:
                break
            ps.setBorderColor(_SLICE_BORDER['disable'])

        if isinstance(pickedObject, QtChart.QPieSlice):
            pickedObject.setBorderColor(_SLICE_BORDER['picked'])

    def fill_slices(self, color: QtGui.QColor):
        for i, ps in enumerate(self.__series.slices()):
            ps.setColor(color)

    @property
    def last_slice(self):
        return self.__last_slice

    def slices(self):
        return self.__series.slices()