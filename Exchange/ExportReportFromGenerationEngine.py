# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import argparse
import ConfigParser
import collections

from library.database  import *
from library.Utils     import *
from Reports.ReportsGenerator.ReportsGeneratorEngine import *

class CReportSetupExport():
    def __init__(self, file):
        self.file = file
        self.fileName = self.getFileName(file)
        self.values = collections.OrderedDict()
        self.loadParams()
        self._reportEngine = CReportsGeneratorEngine()

    def setQueryExecuter(self, db):
        QtGui.qApp.db = db
        self._reportEngine.setQueryExecuter(db.query)


    def getFileName(self, file):
        file = file.strip().split(".")
        return file[0]

    def loadParams(self):
        config = ConfigParser.ConfigParser()
        with codecs.open(self.fileName + '.ini', 'r', 'utf-8') as loadFile:
            config.readfp(loadFile)
            for section in config.sections():
                self.values[section] = config.get(section, "value")

    def findKey(self, dic, value):
        for key in dic.keys():
            if value in key:
                return key
        return None

    def formatDate(self, value):
        return QDate.fromString(value,  "dd.MM.yyyy")

    def formatDateTime(self, value):
        return QDateTime.fromString(value,  "dd.MM.yyyy hh:mm:ss")

    def setData(self, type, value):
        dt = None
        try:
            if type == 'date':
                dt = self.formatDate(value)
            elif type == 'datetime':
                dt = self.formatDateTime(value)
            elif type == 'int':
                return int(value)
            elif type == 'float':
                return float(value)
            else:
                return value
        except ValueError:
            print 'ValueError: ' + type + ' format conversion error'
        if dt.isNull():
            print 'ValueError: ' + type + ' format conversion error'
            exit(1)
        else:
            return dt

    def parametersModel(self):
        if self._reportEngine.loadTemplateFromFile(self.file):
            model = self._reportEngine._parametersModel
            parameters = model.itemsAsDict()
            for index, value in enumerate(self.values.keys()):
                key = self.findKey(parameters, value)
                if key:
                    parameters[key] = self.setData(model._paramList[index]._typeName, self.values[value])
                    model.setItemValues(parameters)
        else:
            self._reportEngine.clear()


    def export(self):
        self.parametersModel()
        doc = self._reportEngine.buildDocument("params", False)
        writer = QtGui.QTextDocumentWriter(self.fileName + '.xls', "html")
        if not writer.write(doc):
            print forceString(writer.device().errorString())
            exit(1)



# *****************************************************************************************

def createParser():
    parser = argparse.ArgumentParser(description = 'Export reports from reports generator engine, the parameters of which are contained in the ini-file. Format of ini-file: [parameter] value = ')
    parser.add_argument('-u', dest = 'user', default = 'dbuser')
    parser.add_argument('-P', dest = 'password')
    parser.add_argument('-t', dest = 'datetime', default = None)
    parser.add_argument('-a', dest = 'host', default = '127.0.0.1')
    parser.add_argument('-p', dest = 'port', type = int, default = '3306')
    parser.add_argument('-d', dest = 'database', default = 's11')
    parser.add_argument('file')
    return parser

def main():
    parser = createParser()
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'ASOV',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    report = CReportSetupExport(args['file'])
    report.setQueryExecuter(db)
    report.export()

if __name__ == '__main__':
    main()