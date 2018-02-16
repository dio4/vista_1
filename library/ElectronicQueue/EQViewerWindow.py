# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

__author__ = 'atronah'

'''
    author: atronah
    date:   30.09.2014
    reason: To display eq info on monitor.
'''

class CEQViewerWindow(QtGui.QMainWindow):
    def __init__(self, parent = None, flags = QtCore.Qt.Window):
        super(CEQViewerWindow, self).__init__(parent)

        self.setupUi(self)


        self._rowCount = 1
        self._columnCount = 1

        self.setCentralWidget(QtGui.QWidget(self))

        self._blockList = []

    @staticmethod
    def setupUi(window):
        # нагло спер из результата работы UIC, ибо форма слишком мелкая, чтобы ради нее 2 файла тянуть
        window.setObjectName("QEMonitorWindow")
        window.setWindowTitle(u'Состояние очередей')
        window.resize(634, 335)
        window.centralwidget = QtGui.QWidget(window)
        window.centralwidget.setObjectName("centralwidget")
        window.gridLayout = QtGui.QGridLayout(window.centralwidget)
        window.gridLayout.setObjectName("gridLayout")
        window.setCentralWidget(window.centralwidget)
        window.toolBar = QtGui.QToolBar(window)
        window.toolBar.setObjectName("toolBar")
        window.addToolBar(QtCore.Qt.TopToolBarArea, window.toolBar)
        window.actFullScreen = QtGui.QAction(window)
        window.actFullScreen.setObjectName("actFullScreen")

        window.toolBar.addAction(u'Полноэкранный режим', window.on_actFullScreen_triggered)

        QtCore.QMetaObject.connectSlotsByName(window)



    @QtCore.pyqtSlot()
    def on_actFullScreen_triggered(self):
        self.switchFullScreen(True)


    def rowCount(self):
        return self._rowCount


    def setRowCount(self, rowCount):
        if 0 < rowCount != self._rowCount:
            self._rowCount = rowCount
            self.rearrange()


    def columnCount(self):
        return self._columnCount


    def setColumnCount(self, columnCount):
        if 0 < columnCount != self._columnCount:
            self._columnCount = columnCount
            self.rearrange()



    def addBlock(self, waitersModel, inProgressModelList):
        gb = QtGui.QGroupBox(waitersModel.queueName())
        gb.setAlignment(QtCore.Qt.AlignCenter)
        font = gb.font()
        font.setPixelSize(32)
        gb.setFont(font)
        layout = QtGui.QGridLayout()

        for column, model in enumerate(inProgressModelList):
            tableView = QtGui.QTableView()
            layout.addWidget(tableView, 0, column)
            tableView.setModel(model)
            tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
            tableView.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
            tableView.verticalHeader().hide()

        label = QtGui.QLabel(u'Приготовится к вызову пациентам с номерами')
        font = label.font()
        font.setPixelSize(32)
        label.setFont(font)
        layout.addWidget(label, 1, 0, 1, len(inProgressModelList), QtCore.Qt.AlignCenter)

        tableView = QtGui.QTableView()
        layout.addWidget(tableView, 2, 0, 1, len(inProgressModelList))
        tableView.setModel(waitersModel)
        tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        tableView.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        tableView.verticalHeader().hide()
        tableView.horizontalHeader().hide()

        gb.setLayout(layout)

        self._blockList.append(gb)




    def clear(self):
        self._blockList = []
        self.rearrange()


    def rearrange(self):
        gridLayout = QtGui.QGridLayout()
        row = 0
        column = 0
        # column += 1 #debug: atronah:
        # btn = QtGui.QPushButton('test') #debug: atronah:
        # gridLayout.addWidget(btn) #debug: atronah:
        for block in self._blockList:
            if column >= self._columnCount:
                row += 1
                column = 0
            if row >= self._rowCount:
                break

            spacer = QtGui.QSpacerItem(30, block.height())
            gridLayout.addWidget(block, row, column * 2)
            gridLayout.addItem(spacer, row, column * 2 + 1)
            column += 1

        newCentralWidget = QtGui.QWidget()
        newCentralWidget.setLayout(gridLayout)
        self.setCentralWidget(newCentralWidget)



    def switchFullScreen(self, enabled):
        newState = QtCore.Qt.WindowFullScreen | self.windowState() if enabled \
                                                                      else self.windowState() & ~QtCore.Qt.WindowFullScreen
        self.setWindowState(newState)
        self.toolBar.setVisible(not enabled)


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape and self.isFullScreen():
            self.switchFullScreen(False)




# class CEQueueViewBlock(QtGui.QGroupBox):
#     def __init__(self, title, parent = None):
#         super(CEQueueViewBlock, self).__init__(title, parent)
#         self._inProgressViewList = []
#         self._waitersViewList = []
#
#
#     def initBlock(self, waitersModel, inProgressModelList):
#         layout = QtGui.QGridLayout()
#
#
#
#
#     def setModel(self, model):
#         super(CEQueueView, self).setModel(model)
#         model.rowsInserted.connect(self.updateSize)
#
#
#
#
#     @QtCore.pyqtSlot()
#     def updateSize(self):
#         model = self.model()
#         newSize = QtCore.QSize(self.verticalHeader().width() + (model.columnCount() + 1) * self.frameWidth() + sum([self.horizontalHeader().sectionSize(i) for i in xrange(model.columnCount())]),
#                       self.horizontalHeader().height() + (model.rowCount() + 1) * self.frameWidth() + self.verticalHeader().sectionSize(0) * model.rowCount())
#         if newSize.width() > self._maxSize.width() \
#                 or newSize.height() > self._maxSize.height():
#             self._maxSize = newSize
#             self.setMinimumSize(newSize)
#             self.setMaximumSize(newSize)
#             self.updateGeometry()



def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    w = CEQViewerWindow()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()