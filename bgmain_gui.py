#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:25:43 2022.

a pyQt module to plot arterial blood gases

@author: cdesbois
"""
import os
import sys
import copy
import logging
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QAction,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QSizePolicy,
    QFileDialog,
    QTextEdit,
)

import bgplot

logfile = os.path.expanduser(os.path.join("~", "blood_gases.log"))
logging.basicConfig(
    level=logging.INFO,
    force=True,
    format="%(levelname)s:%(funcName)s:%(message)s",
    filename=logfile,
    filemode="w+",
    # handlers=[logging.FileHandler(logfile)],
)

# initialise the 'gases' list and add a fisrt reference value g0
# initialise a 'gasesV' visualisation dictionary to see the object in spyder
gases, gasesV = [], {}
g0 = bgplot.Gas(spec="horse")
gases.append(g0)
gasesV["g0"] = g0.__dict__

# buildTestSet2(reset=True, addNewG=False)


class SelectGas(QWidget):
    """
    Qwidget to create new gas values (Gas class).

    NB add them in the bloodGases list ('gases') and dictionary ('gasesV').
    """

    #    def __init__(self): #, gases, gasesV):
    def __init__(self) -> None:
        # print('SelectGas init')
        super().__init__()
        global gases, gasesV
        self.title = "gas" + str(len(gases) - 1)
        self.left = 15
        self.top = 10
        self.width = 140
        self.height = 450
        self.gases = gases
        self.gasesV = gasesV
        self.num = len(gases) - 1
        self.tot = len(gases)
        self.bgObj = copy.deepcopy(gases[self.num])
        self.gasKey = [
            "num",
            "spec",
            "hb",
            "fio2",
            "po2",
            "ph",
            "pco2",
            "hco3",
            "etco2",
        ]
        # self.gasVal = {}  # to record displayed values

        # self.update_Values(self.num)
        self.defaults_Values(0)
        self.init_UI()

    def init_UI(self) -> None:
        """Initialise."""
        self.create_Table()
        self.create_ButtonsGrid()
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self.tableWidget)
        vbox.addLayout(self.gasBox)
        # sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.setLayout(vbox)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedWidth(self.width)
        # sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.setSizePolicy(sizePolicy)
        self.show()

    def create_ButtonsGrid(self) -> None:
        """Create buttons."""
        # print("f=create_ButtonsGrid")
        prevBut = QPushButton("prevGas")
        prevBut.setToolTip("previous gas")
        prevBut.setMinimumWidth(0)
        prevBut.clicked.connect(self.prev_gas)
        nextBut = QPushButton("nextGas")
        nextBut.setToolTip("next gas")
        nextBut.setMinimumWidth(0)
        nextBut.clicked.connect(self.next_gas)
        newGBut = QPushButton("createNewGas", self)
        newGBut.setToolTip("to fill the new Values in a new gas record")
        newGBut.setMinimumWidth(0)
        newGBut.clicked.connect(self.new_Gas)
        #        exampleFile = QPushButton('exampleFile')
        #        exampleFile.setMinimumWidth(0)
        #        exampleFile.clicked.connect(self.load_example)
        self.gasBox = QVBoxLayout()
        self.gasBox.addWidget(prevBut)
        self.gasBox.addWidget(nextBut)
        self.gasBox.addWidget(newGBut)
        # self.gasBox.addWidget(exampleFile)

    def defaults_Values(self, num: int = 0) -> None:
        """Defaults."""
        # print('f= defaults_Values')
        self.bgObj = copy.deepcopy(self.gases[num])
        self.num = num
        for key in self.gasKey:
            if key != "num":
                setattr(self, key, getattr(self.bgObj, key))

    def create_Table(self) -> None:
        """Build Table."""
        # print('f=create_Table')
        # val = ['num', 'spec', 'hb','fio2','po2','ph','pco2','hco3','etco2']
        self.tableWidget = QTableWidget(len(self.gasKey), 1)
        self.tableWidget.title = self.title
        self.tableWidget.setHorizontalHeaderLabels(["value"])
        self.tableWidget.setVerticalHeaderLabels(self.gasKey)
        for n, item in enumerate(self.gasKey):
            newItem = QTableWidgetItem(str(getattr(self, item)))
            self.tableWidget.setItem(n, 0, newItem)

    def print_gas(self, name: str) -> None:
        """
        Print the values in self.key, self.gasVal[key], and self.obj[key].

        removed gasVal in this version (not needed)
        """
        print("\n", name)
        print("key", "\t", "self.key", "self.obj[key]")
        for key in self.gasKey:
            if key == "num":
                print(
                    key, "\t", getattr(self, key), "\t \t", "total= ", len(self.gases)
                )
            else:
                print(key, "\t", getattr(self, key), "\t\t", getattr(self.bgObj, key))

    def self_to_table(self) -> None:
        """Self.attr to table."""
        # print('f=self_to_table')
        # self.print_gas('before updateTable')
        for n, item in enumerate(self.gasKey):
            self.tableWidget.item(n, 0).setText(str(getattr(self, item)))
        # self.print_gas('after updateTable')

    def table_to_self(self, num: int) -> None:
        """Table to self."""
        # print('f=table_to_self')
        self.num = len(gases)
        self.spec = str(self.tableWidget.item(1, 0).text())
        for i, key in enumerate(self.gasKey[2:]):
            # replace ',' by '.' for float conversion
            val = self.tableWidget.item(i + 2, 0).text().replace(",", ".")
            setattr(self, key, float(val))

    def self_to_selfObj(self, num: int) -> None:
        """Self_to_selfObj."""
        # print('f=self_to_selfObj')
        for key in self.gasKey:
            if key != "num":
                setattr(self.bgObj, key, getattr(self, key))

    def selfObj_to_self(self, num: int) -> None:
        """SelfObj_to_self."""
        # print('f=selfObj_to_self')
        self.bgObj = copy.deepcopy(self.gases[num])
        self.num = num
        for key in self.gasKey:
            if key != "num":
                setattr(self, key, getattr(self.bgObj, key))

    @pyqtSlot()
    def change_gas(self, num: int = 0) -> None:
        # print('f=change_gas')
        """
        Change obj from gases[num].

        & update the self.value parameters.
        """
        # print('\n', "f=update_Values, targetNum= ", num, 'currentNum= ', self.num)
        # self.print_gas('changeGas before')
        self.bgObj = copy.deepcopy(self.gases[num])
        self.num = num
        for key in self.gasKey:
            if key != "num":
                setattr(self, key, getattr(self.bgObj, key))
            else:
                pass
        # self.print_gas("changeGas after")

    @pyqtSlot()
    def prev_gas(self) -> None:
        """Get the previous gas."""
        # print("f=prev_gas")
        # self.print_gas('before previous gas')
        num = self.num
        # print("self.num= ", num, "len(gases) = ", len(gases))

        if num > 0:
            num -= 1
            # print('change_gas(', num, ')')
            self.selfObj_to_self(num)
            self.self_to_table()
        #            self.print_gas('after previous gas')
        else:
            QMessageBox.information(self, "str", " this is already the first gas")

    @pyqtSlot()
    def next_gas(self) -> None:
        """Get the next gas."""
        num = self.num
        # print('f=next_gas')
        # print("self.num= ", num, "len(gases) = ", len(gases))
        # self.print_gas('before previous gas')

        if self.num == (len(gases) - 1):
            QMessageBox.information(self, "str", " this is already the last gas")
        else:
            num += 1
            # print('change_gas(', num, ')')
            self.selfObj_to_self(num)
            self.self_to_table()
            # print('self values after')

    @pyqtSlot()
    def new_Gas(self) -> None:
        """
        Create a new gas, append it to the gasesList and gasesVDict.

        incremented num (to put at the end of the gases list)
        update the selfValues
        update the Table
        """
        # print( 'f=new_Gas',
        # "self.num= ", self.num, "len(gases) = ", len(gases))

        num = len(self.gases)  # ie gas +1 (list begin with 0)

        # Table to attributes (update self.attributes and gasValList)
        self.table_to_self(num)
        # self.attr to gasObj (build GasObg, and add to the gasesList)
        dico = dict(
            spec=self.spec,
            hb=self.hb,
            fio2=self.fio2,
            po2=self.po2,
            ph=self.ph,
            pco2=self.pco2,
            hco3=self.hco3,
            etco2=self.etco2,
        )

        newBgObj = bgplot.Gas(**dico)
        # newBgObj = bgplot.Gas(self.spec, self.hb, self.fio2, self.po2,
        #                   self.ph, self.pco2, self.hco3, self.etco2)
        self.gases.append(newBgObj)

        # add to the gasesV dicionary (of gasObj__dict__)
        name = "g" + str(self.num)
        self.gasesV[name] = newBgObj.__dict__

        res = (
            "added gas="
            + str(self.num)
            + " spec="
            + self.spec
            + " hb="
            + str(self.hb)
            + " fio2="
            + str(self.fio2)
            + " po2="
            + str(self.po2)
            + " ph="
            + str(self.ph)
            + " pco2="
            + str(self.pco2)
            + " hco3="
            + str(self.hco3)
            + " etco2="
            + str(self.etco2)
        )
        # print(res)
        logging.warning(res)

        # update self.Obj values
        # self_to_selfObj(self.num)   # TODO : doesnt work if extracted from this function
        self.bgObj = copy.deepcopy(self.gases[num])
        for key in self.gasKey:
            if key != "num":
                setattr(self.bgObj, key, getattr(self, key))
        # self.print_gas('newGas after self.obj changed')

        # update table values displayed
        self.self_to_table()
        # self.print_gas('newGas after update_Table')

        # print('newGas= ', self.num, 'over a total of ', len(gases))

    # update the reference values (obj attribute) ? unnecessary
    # self.updateValues(self.num)


#    @pyqtSlot()
#    def load_example(self):
#        global gases, gasesV
#        # reset the lists and add a reference
#        #self.gas = SelectGas() # reset
#        print ('len(gases)=',len(gases))
#        self.gases, self.gasesV = [], {}
#        g0 = bgplot.Gas()
#        self.gases.append(g0)
#        self.gasesV['g0'] = g0
#
#        #file ='example.csv'
#        file = os.path.join(sys.path[0], 'example.csv')
#        print(file)
#        #titles = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3']
#        default= ['horse', 12  , 0.21, 100,     7.4,    40,     24]
#        #load the data
#        with open(file) as csvfile:
#            reader = csv.reader(csvfile, delimiter='\t')
#            next(reader, None)  # skip the firstLine
#            k = 1
#            for row in reader:
#                for i,item in enumerate(row):
#                    row[i] = row[i].replace(",",".")
#                    row[i] = row[i].replace(" ","")
#                    # replace empty spec
#                    if len(row[0]) == 0:
#                        row[0] = 'dog'
#                    # tranform string to floats
#                    if i>0:
#                        try:
#                            dec = row[i]
#                            dec = float(dec)
#                            row[i] = dec
#                        except ValueError:
#                            # print('i=', i, ' ', item, ' row[i]=', row[i],
#                            #    type(row[i]), 'len=',len(row[i]))
#                            row[i] = None
#                        if row[i] in (None, ""):
#                            row[i] = default[i]
#                # implement variables
#                spec =  row[0]
#                hb =    row[1]
#                fio2 =  row[2]
#                po2 =   row[3]
#                ph =    row[4]
#                pco2 =  row[5]
#                hco3 =  row[6]
#                # build gasObj
#                sample = bgplot.Gas(spec, hb, fio2, po2, ph, pco2, hco3)
#                self.gases.append(copy.deepcopy(sample))
#                name = 'g' + str(k)
#                self.gasesV[name]= sample.__dict__
#                print('k=', k, 'len(gases)=', len(self.gases))
#                k += 1
#                #print ('spec=', spec, 'hb=', hb ,'fio2=', fio2, 'po2=', po2,
#                #         'ph=', ph, 'pco2=', pco2, 'hco3=', hco3)
#                # print ('spec=', type(spec), 'hb=', type(hb) ,'fio2=',
#                           type(fio2), 'po2=', type(po2),
#                #         'ph=', type(ph), 'pco2=', type(pco2), 'hco3=',
#               type(hco3))
#
#            print ("added ", len(self.gases), 'gases to gases and gasesV')
#
#        self.change_gas(1)
# update the self.bgObj values
# self.gas.change_gas(self)
# num = 0
# self.num = 0
# self.bgObj = copy.deepcopy(self.gases[num])
# for key in self.gasKey:
#     if key != 'num':
#         setattr(self.bgObj, key, getattr(self, key))
# # self.print_gas('newGas after self.obj changed')
# # update table values displayed
# self.self_to_table()

#   loadDataFile('example.csv')


#    @pyqtSlot()  # create the method
#    def close_Window(self):
#        print('f close_Window')
#        self.close()
# app.setQuitOnLastWindowClosed(False)
# app.exit()  # doesn't work
# QCoreApplication.exit()
# QCoreApplication.instance().quit

#       @pyqtSlot()
#       def on_click(self):
#           print("\n")
#           for currentQTableWidgetItem in self.tableWidget.selectedItems():
#               print(currentQTableWidgetItem.row(),
#                   currentQTableWidgetItem.column(),
#                   currentQTableWidgetItem.text())


# if __name__ == '__main__':
#    app = QApplication(sys.argv)
#    ex = App()
#    app.aboutToQuit.connect(app.deleteLater)
#   sys.exit(app.exec_())

# see http://stackoverflow.com/questions/10888045/
# simple-ipython-example-raises-exception-on-sys-exit


# ==============================================================================
# if __name__ == '__main__':
#     app = QApplication.instance()  # checks if QApplication already exists
#     if not app:  # create QApplication if it doesnt exist
#         app = QApplication(sys.argv)
#     #ex = SelectGas(gases, gasesV)
#     ex = SelectGas()
#     app.exec_()
# ==============================================================================
# app.aboutToQuit.connect(app.deleteLater)
#
# %% to plot the results using pyQt

# TODO (cf /Volumes/USERS/cdesbois/pg/toPlay/qt/test3.py):
#   1- DONE change bloodGases2 to return objects and remove plt
#   2- DONE modify the pyQt program to be able to use the 'gases' list
#   3- DONE add a list of all the graph to be displayed
#   4- DONE associate the two qt program in the same MainWindow
#   5- DONE choose a bloogas to plot
#   6- DONE interaction between the two widgets
#   7- DONE program a plot to display the velues (starting point to teach)
#   8- DONE load a file for training data
#   9- implement the save function
#   10- implement the 'choose parameters' function (the graphs to be displayed)

# nb see http://stackoverflow.com/questions/31611188/
# why-does-matplotlib-figure-figure-behave-so-different-than-matplotlib-pyplot-fig
# ===============================================================================
# to import the Figure in a QT Widget
# for command-line arguments
class Qt5MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget."""

    def __init__(self, parent: Any, fig: plt.Figure) -> None:
        # print('f=Qt5MplCanvas init')
        # plot definition
        self.fig = fig
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set the parent widget
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        # we define the widget as expandable
        # FigureCanvas.setSizePolicy(self,
        #                            QSizePolicy.Expanding,
        #                            QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def redraw(self, fig: plt.Figure) -> None:
        """Redraw the canvas."""
        # print('f = redraw')
        self.fig = fig
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        # self.setParent(parent)
        # FigureCanvas.setSizePolicy(self,
        #                            QSizePolicy.Expanding,
        #                            QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)


class ApplicationWindow(QMainWindow):
    """Example main window."""

    def __init__(self) -> None:
        # print('f=ApplicationWindow init')
        QMainWindow.__init__(self)
        self.setGeometry(50, 50, 1400, 800)
        self.setWindowTitle("example")
        self.statusBar()
        # QAction (for menuBar)
        openFile = QAction("&open file", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("open a record")
        openFile.triggered.connect(self.file_open)
        #        loadExample = QAction("&load Example", self)
        #        loadExample.setStatusTip("example File")
        #        loadExample.triggered.connect(self.load_example)
        closeApp = QAction("&close", self)
        closeApp.setShortcut("Ctrl+Q")
        closeApp.setStatusTip("leave the application")
        closeApp.triggered.connect(self.close_application)
        # create a menuBar
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)  # for macintosh
        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(openFile)
        #        fileMenu.addAction(loadExample)
        fileMenu.addAction(closeApp)
        self.plotNum = 0
        self.fig = Figure()
        self.assign_central_Widget()
        self.home()

    def assign_central_Widget(self) -> None:
        """Central window."""
        # print('f=assign_central_Widget')
        # mainWidget
        self.main_widget = QWidget(self)
        self.hbl = QHBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt5MplCanvas(self.main_widget, self.fig)
        # self.gas = SelectGas(gases, gasesV)
        self.gas = SelectGas()  # reset des valeurs
        # instantiate the navigation toolbar
        # self.ntb = NavigationToolbar(self.qmc, self.main_widget)
        # pack these widget into the vertical box
        self.hbl.addWidget(self.gas)
        self.hbl.addWidget(self.qmc)
        # set the focus on the main widget
        self.main_widget.setFocus()
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)

    def update_central_widget(self) -> None:
        """Update the central widget."""
        # print('f=update_central_widget')
        self.main_widget = QWidget(self)
        self.hbl = QHBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt5MplCanvas(self.main_widget, self.fig)
        # self.ntb = NavigationToolbar(self.qmc, self.main_widget)
        self.hbl.addWidget(self.gas)
        self.hbl.addWidget(self.qmc)
        self.main_widget.setFocus()
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)

    def home(self) -> None:
        """Build the buttons for the toolbar."""
        # print('f=home')
        # buttons for the toolBar
        buildPlots = QAction("build plots", self)
        buildPlots.triggered.connect(self.build_plots)
        previousP = QAction("previous", self)
        previousP.triggered.connect(self.previous_plot)
        nextP = QAction("next", self)
        nextP.triggered.connect(self.next_plot)
        selectParams = QAction("chooseParams", self)
        selectParams.triggered.connect(self.choose_params)
        # toolBar
        self.toolBar = self.addToolBar("navigate")
        self.toolBar.addAction(buildPlots)
        self.toolBar.addAction(previousP)
        self.toolBar.addAction(nextP)
        self.toolBar.addAction(selectParams)

    def build_plots(
        self,
        plotNum: int = 0,
        case: str = "clin",
        path: str = "toto",
        save: bool = False,
        ident: str = "",
        pyplot: bool = False,
    ) -> None:
        """Build the plots."""
        self.plotNum = plotNum  # reset the plot count
        # num = self.gas.num
        # gases = copy.deepcopy(self.gas.gases)  # ??? needed
        self.plotObjList: list[Any] = []
        # print('sending num=', num, 'hb=', gases[num].hb)
        self.select_plots(
            "clin", self.gas.gases, self.gas.num, path, ident, save, pyplot
        )
        # print('sending num=', num)
        self.fig = self.plotObjList[self.plotNum]
        self.update_central_widget()

    def previous_plot(self) -> None:
        """Move to previous plot."""
        # print('f=previous_plot')
        # try:
        #     plotNum
        # except NameError:
        #     msgBox = QMessageBox.information(self, 'str',
        #             "you have to 'build plots' before to navigate")
        #     return
        if self.plotNum > 0:
            self.plotNum -= 1
            self.fig = self.plotObjList[self.plotNum]
            self.update_central_widget()
        else:
            QMessageBox.information(self, "str", "this is already the first plot")

    def next_plot(self) -> None:
        """Move to the next plot."""
        # print('f=next_plot')
        # try:
        #     plotObjList
        # except NameError:
        #     msgBox = QMessageBox.information(self, 'str',
        #             "you have to 'build plots' before to navigate")
        #     return

        if self.plotNum < (len(self.plotObjList) - 1):
            self.plotNum += 1
            self.fig = self.plotObjList[self.plotNum]
            self.update_central_widget()
        else:
            QMessageBox.information(self, "str", "this is the last plot")

    def choose_params(self) -> None:
        """Unused."""
        pass

    def close_application(self) -> None:
        """Close the application."""
        # print('f=close_application')
        choice = QMessageBox.question(
            self,
            "Extract",
            "Do you really want to quit ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def editor(self) -> None:
        """Put the texedit in the central widget."""
        self.texEdit = QTextEdit()
        self.setCentralWidget(self.texEdit)

    def file_open(self) -> None:
        """Dialog to open example file."""
        fname = QFileDialog.getOpenFileName(self, "Open File", "")
        if fname[0]:
            f = open(fname[0], "r")
            self.editor()
            with f:
                text = f.read()
                self.texEdit.setText(text)

    def plot_now(
        self,
        name: str,
        gases: Any,
        num: int,
        path: str,
        ident: str,
        save: bool,
        pyplot: bool,
        pcent: bool,
    ) -> None:
        """Generate the plots."""
        plotList = [
            "display",
            "morpion",
            "acidBAse",
            "o2",
            "ventil",
            "sat",
            "cao2",
            "hbEffect",
            "varCaO2",
            "pieCasc",
            "cascO2",
            "gAa",
            "GAaRatio",
            "ratio",
        ]
        # print(name)
        if name not in plotList:
            print("the resquested plot should be in ", plotList)
            return
        if pyplot is False:
            logging.warning(f"{name=} {len(gases)=}, {num=}")
            if name == "display":
                self.plotObjList.append(
                    bgplot.plot_display(gases, num, path, ident, save, pyplot)
                )
            if name == "morpion":
                self.plotObjList.append(
                    bgplot.plot_morpion(gases, num, path, ident, save, pyplot)
                )
            if name == "acidBAse":
                self.plotObjList.append(
                    bgplot.plot_acidbas(gases, num, path, ident, save, pyplot)
                )
            if name == "o2":
                self.plotObjList.append(
                    bgplot.plot_o2(gases, num, path, ident, save, pyplot)
                )
            if name == "ventil":
                self.plotObjList.append(
                    bgplot.plot_ventil(gases, num, path, ident, save, pyplot)
                )
            if name == "sat":
                self.plotObjList.append(
                    bgplot.plot_satHb(gases, num, path, ident, save, pyplot)
                )
            if name == "cao2":
                self.plotObjList.append(
                    bgplot.plot_CaO2(gases, num, path, ident, save, pyplot)
                )
            if name == "hbEffect":
                self.plotObjList.append(
                    bgplot.plot_hbEffect(gases, num, path, ident, save, pyplot)
                )
            if name == "varCaO2":
                self.plotObjList.append(
                    bgplot.plot_varCaO2(gases, num, path, ident, save, pyplot)
                )
            if name == "pieCasc":
                self.plotObjList.append(
                    bgplot.plot_pieCasc(gases, num, path, ident, save, True, pyplot)
                )
                self.plotObjList.append(
                    bgplot.plot_pieCasc(gases, num, path, ident, save, False, pyplot)
                )
            if name == "cascO2":
                if num == 0:
                    self.plotObjList.append(
                        bgplot.plot_cascO2Lin(gases, [0], path, ident, save, pyplot)
                    )
                #                self.plotObjList.append(bgplot.plot_cascO2(gases, \
                # [0,len(gases)-1], path, ident, save, pyplot))
                #                self.plotObjList.append(bgplot.plot_cascO2Lin(gases, \
                # [0,len(gases)-1], path, ident, save, pyplot))
                else:
                    self.plotObjList.append(
                        bgplot.plot_cascO2Lin(
                            gases, list(range(len(gases))), path, ident, save, pyplot
                        )
                    )
            if name == "gAa":
                self.plotObjList.append(
                    bgplot.plot_GAa(gases, num, path, ident, save, pyplot)
                )
            if name == "GAaRatio":
                self.plotObjList.append(
                    bgplot.plot_GAaRatio(gases, num, path, ident, save, pyplot)
                )
            if name == "ratio":
                self.plotObjList.append(
                    bgplot.plot_ratio(gases, num, path, ident, save, pyplot)
                )
            # print('len(self.plotObjList=', len(self.plotObjList))
        #            for fig in self.plotObjList:
        #                fig.set_tight_layout(False)

        else:
            if name == "display":
                bgplot.plot_display(gases, num, path, ident, save, pyplot)
            if name == "morpion":
                bgplot.plot_morpion(gases, num, path, ident, save, pyplot)
            if name == "acidBAse":
                bgplot.plot_acidbas(gases, num, path, ident, save, pyplot)
            if name == "o2":
                bgplot.plot_o2(gases, num, path, ident, save, pyplot)
            if name == "ventil":
                bgplot.plot_ventil(gases, num, path, ident, save, pyplot)
            if name == "sat":
                bgplot.plot_satHb(gases, num, path, ident, save, pyplot)
            if name == "cao2":
                bgplot.plot_CaO2(gases, num, path, ident, save, pyplot)
            if name == "hbEffect":
                bgplot.plot_hbEffect(gases, num, path, ident, save, pyplot)
            if name == "varCaO2":
                bgplot.plot_varCaO2(gases, num, path, ident, save, pyplot)
            if name == "pieCasc":
                bgplot.plot_pieCasc(gases, num, path, ident, save, True, pyplot)
                bgplot.plot_pieCasc(gases, num, path, ident, save, False, pyplot)
            if name == "cascO2":
                # bgplot.plot_cascO2(gases, [0, len(gases)-1], path, ident, save, pyplot)
                # bgplot.plot_cascO2Lin(gases, [0, len(gases)-1], path, ident, save, pyplot)
                bgplot.plot_cascO2Lin(
                    gases, list(range(len(gases))), path, ident, save, pyplot
                )
            if name == "gAa":
                bgplot.plot_GAa(gases, num, path, ident, save, pyplot)
            if name == "GAaRatio":
                bgplot.plot_GAaRatio(gases, num, path, ident, save, pyplot)
            if name == "ratio":
                bgplot.plot_ratio(gases, num, path, ident, save, pyplot)

    def select_plots(
        self,
        name: str,
        gases: Any,
        num: int,
        path: str,
        ident: str,
        save: bool,
        pyplot: bool,
    ) -> list[str]:
        """Select the plots to be build."""
        # print('f select_plots')
        pcent = False
        selections = {}
        selections["all"] = [
            "display",
            "morpion",
            "acidBAse",
            "o2",
            "ventil",
            "sat",
            "cao2",
            "hbEffect",
            "varCaO2",
            "pieCasc",
            "cascO2",
            "gAa",
            "GAaRatio",
            "ratio",
        ]
        selections["clin"] = [
            "display",
            "morpion",
            "acidBAse",
            "ventil",
            "sat",
            "cao2",
            "hbEffect",
            "varCaO2",
            "pieCasc",
            "cascO2",
            "GAaRatio",
        ]

        if name == "all":
            selection = selections["all"]
        elif name == "clin":
            selection = selections["clin"]
        else:
            print("name shoud be 'all' or 'clin'")
            selection = []

        for item in selection:
            self.plot_now(item, gases, num, path, ident, save, pyplot, pcent)
        return selection

    # select_plots('clin', gases, num, path, ident, save, pyplot)


##############################################################################

# ==============================================================================
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     aw = ApplicationWindow()
#     aw.setWindowTitle("test")
#     aw.show()
#     #sys.exit(qApp.exec_())
#     app.exec_()
#
# ==============================================================================

# check https://stackoverflow.com/questions/58671506/qapplication-and-main-window-connection

if __name__ == "__main__":
    app = QApplication.instance()  # checks if QApplication already exists
    if app is None:  # create QApplication if it doesnt exist
        app = QApplication(sys.argv)
    # ex = SelectGas(gases, gasesV)
    # ex = Gas()
    aw = ApplicationWindow()
    aw.show()
    #
    app.exec_()
