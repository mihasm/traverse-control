from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QTextStream, pyqtSignal, QProcess, QRect
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QComboBox,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QGridLayout,
    QCheckBox,
    QStyleFactory,
    QMessageBox,
    QAction,
    QFileDialog,
)

import numpy
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

from numpy import arange, sin, pi
from functools import partial
import matplotlib.pyplot as plt


"""
data = {}

for line in f.readlines()[1:]:
    #print(line.strip())
    x,y,z,date,vel,vel_u,temp,temp_u,perc,perc_str = line.strip()[:-1].split(',')
    if not perc_str in data:
        data[perc_str] = []
    data[perc_str].append([x,y,z,date,vel,vel_u,temp,temp_u,perc,perc_str])

by_points = {}

for measurement, raw_data in data.items():
    by_points[measurement] = {}
    for m in raw_data:
        x,y,z,date,vel,vel_u,temp,temp_u,perc,perc_str = m
        x = float(x)
        y = float(y)
        z = float(z)
        if not (x,y,z) in by_points[measurement]:
            by_points[measurement][(x,y,z)] = []
        by_points[measurement][(x,y,z)].append([date,vel,vel_u,temp,temp_u,perc,perc_str])

averaged = {}

for measurement, data in by_points.items():
    if not measurement in averaged:
        averaged[measurement] = {}
    for point, raw_data in data.items():
        all_speeds = []
        all_temps = []
        for date,vel,vel_u,temp,temp_u,perc,perc_str in raw_data:
            all_speeds.append(vel)
            all_temps.append(temp)
"""


class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        
        self.screen = app.primaryScreen()
        self.size = self.screen.size()
        self.screen_width = self.size.width()
        self.screen_height = self.size.height()
        self.setGeometry(self.screen_width * 0.125, self.screen_height * 0.125, self.screen_width * 0.75, self.screen_height * 0.75)
        self.setWindowTitle('Title')
        self.main_widget = QtWidgets.QWidget(self)
        self.data = {'test1':{'type':'line','x':numpy.array([0,1,2,3,4,5,6]),'y':numpy.sin([0,1,2,3,4,5,6])},
                     'test2':{'type':'line','x':numpy.array([0,1,2,3,4,5,6]),'y':numpy.cos([0,1,2,3,4,5,6])}}
        

        grid = QGridLayout(self.main_widget)

        self.fig = plt.figure(figsize=(10, 5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-1,10)
        self.ax.set_ylim(0,10)


        self.canvas = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(self.canvas,self)


        grid.addWidget(self.canvas,1,1)
        grid.addWidget(toolbar,2,1)

        self.checkboxes = CheckBoxes(self)
        grid.addWidget(self.checkboxes,1,2)
        


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.show()

        #self.redraw()

    def redraw(self):
        self.ax.clear()
        for n,s in self.checkboxes.list_checkboxes:
            if s == True:
                if n in self.data:
                    if self.data[n]['type'] == 'line':
                        x = self.data[n]['x']
                        y = self.data[n]['y']
                        self.draw_line(x,y)

        self.canvas.draw_idle()


    def draw_line(self,*args,**kwargs):
        self.ax.plot(*args,**kwargs)
       



class CheckBoxes(QWidget):
    def __init__(self,main):
        super().__init__()
        self.parent = main
        self.list_checkboxes = []
        self.form = QFormLayout()
        self.setLayout(self.form)
        

        self.add_checkbox('test1')
        self.add_checkbox('test2')
        self.show()

    def add_checkbox(self,name,state=False):
        for n,s in self.list_checkboxes:
            if n == name:
                raise Exception("Name already exists: %s" % name)
        a = QCheckBox(name)
        self.list_checkboxes.append([name,state])
        a.setChecked(state)
        a.stateChanged.connect(partial(self.checkbox_change,name))
        self.form.addWidget(a)

    def remove_checkbox(self,string):
        i=0
        for n,s in self.list_checkboxes:
            if n == string:
                child = self.form.takeAt(i)
                if child.widget():
                  child.widget().deleteLater()
                  del self.list_checkboxes[i]
            i+=1

    def checkbox_change(self,name,state):
        i=0
        for n,s in self.list_checkboxes:
            if n == name:
                self.list_checkboxes[i] = n, self.checkbox_num_to_state(state)
            i+=1
        self.parent.redraw()

    def checkbox_num_to_state(self,num):
        if num == 2:
            return True
        return False


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main = MainWindow(app)
    sys.exit(app.exec_())