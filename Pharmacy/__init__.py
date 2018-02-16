import logging.config
import os
from PyQt4 import QtCore

logDir = os.path.join(unicode(QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())), '.vista-med')

logging.config.dictConfig({
    'version'   : 1,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(name)s] %(message)s'
        }
    },
    'handlers'  : {
        'null'    : {
            'level': 'DEBUG',
            'class': 'logging.NullHandler'
        },
        'errorLog': {
            'level'    : 'ERROR',
            'class'    : 'logging.FileHandler',
            'filename' : os.path.join(logDir, 'pharmacy.error.log'),
            'formatter': 'verbose'
        },
    },
    'loggers'   : {
        'requests.packages.urllib3': {
            'level'    : 'ERROR',
            'propagate': False,
            'handlers' : [
                'errorLog'
                # 'null'
            ]
        }
    }
})
