# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\TissueJournal\LaboratoryCalculator\LaboratoryCalculator.ui'
#
# Created: Fri Jun 15 12:17:35 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(690, 420)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 690, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        self.menu_2 = QtGui.QMenu(self.menubar)
        self.menu_2.setObjectName(_fromUtf8("menu_2"))
        self.menu_3 = QtGui.QMenu(self.menubar)
        self.menu_3.setObjectName(_fromUtf8("menu_3"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actLogin = QtGui.QAction(MainWindow)
        self.actLogin.setObjectName(_fromUtf8("actLogin"))
        self.actLogout = QtGui.QAction(MainWindow)
        self.actLogout.setObjectName(_fromUtf8("actLogout"))
        self.actExit = QtGui.QAction(MainWindow)
        self.actExit.setObjectName(_fromUtf8("actExit"))
        self.actConnection = QtGui.QAction(MainWindow)
        self.actConnection.setObjectName(_fromUtf8("actConnection"))
        self.actAboutQt = QtGui.QAction(MainWindow)
        self.actAboutQt.setObjectName(_fromUtf8("actAboutQt"))
        self.actAbout = QtGui.QAction(MainWindow)
        self.actAbout.setObjectName(_fromUtf8("actAbout"))
        self.actDecor = QtGui.QAction(MainWindow)
        self.actDecor.setObjectName(_fromUtf8("actDecor"))
        self.menu.addAction(self.actLogin)
        self.menu.addAction(self.actLogout)
        self.menu.addSeparator()
        self.menu.addAction(self.actExit)
        self.menu_2.addAction(self.actConnection)
        self.menu_2.addAction(self.actDecor)
        self.menu_3.addAction(self.actAboutQt)
        self.menu_3.addAction(self.actAbout)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.menu.setTitle(QtGui.QApplication.translate("MainWindow", "Меню", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_2.setTitle(QtGui.QApplication.translate("MainWindow", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_3.setTitle(QtGui.QApplication.translate("MainWindow", "Помощь", None, QtGui.QApplication.UnicodeUTF8))
        self.actLogin.setText(QtGui.QApplication.translate("MainWindow", "Подключиться", None, QtGui.QApplication.UnicodeUTF8))
        self.actLogout.setText(QtGui.QApplication.translate("MainWindow", " Отключиться", None, QtGui.QApplication.UnicodeUTF8))
        self.actExit.setText(QtGui.QApplication.translate("MainWindow", " Выйти", None, QtGui.QApplication.UnicodeUTF8))
        self.actConnection.setText(QtGui.QApplication.translate("MainWindow", "База данных", None, QtGui.QApplication.UnicodeUTF8))
        self.actAboutQt.setText(QtGui.QApplication.translate("MainWindow", "О Qt", None, QtGui.QApplication.UnicodeUTF8))
        self.actAbout.setText(QtGui.QApplication.translate("MainWindow", "О программе", None, QtGui.QApplication.UnicodeUTF8))
        self.actDecor.setText(QtGui.QApplication.translate("MainWindow", "Внешний вид", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

