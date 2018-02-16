# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Action import CJobTicketActionPropertyValueType, CRLSExtendedActionPropertyValueType
from Events.ActionPropertyChooser import CActionPropertyChooser
from PropertyHistoryDialog import CPropertyHistoryDialog
from Users.Rights import urModifyObsoleteQuotas
from library.ExtendedTableView import CExtendedTableView
from library.PreferencesMixin import CPreferencesMixin
from library.Utils import foldText, forceDate, forceInt, forceRef, forceString, forceStringEx, getPref, setPref, toVariant
from library.crbcombobox import CRBModelDataCache


class CActionPropertiesTableModel(QtCore.QAbstractTableModel):
    __pyqtSignals__ = ('actionNameChanged()',
                       'setCurrentActionEndDate(QDate)',
                      )

    class PropertyShowType:
        Show = 0
        ReadOnly = 1
        Hide = 2

    propertyValueChanged = QtCore.pyqtSignal(QtCore.QString, QtCore.QVariant, QtCore.QVariant)  # name, oldValue, newValue

    column = [u'Назначено', u'Значение',  u'Ед.изм.',  u'Норма', u'Оценка']
    visibleAll = 0
    visibleInJobTicket = 1
    ciIsAssigned   = 0
    ciValue      = 1
    ciUnit       = 2
    ciNorm       = 3
    ciEvaluation = 4

    def __init__(self, parent, visibilityFilter=0):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.action = None
        self.clientId = None
        self._rowDataList = []
        self.unitData = CRBModelDataCache.getData('rbUnit', True)
        self.visibilityFilter = visibilityFilter
        self.readOnly = False
        self.actionStatusTip = None

        self._spanInfo = []

        self.propertyValueChanged.connect(self.notifyProperties)

    def notifyProperties(self, propertyName, oldValue, newValue):
        for propertyType in self.propertyTypeList:
            valueType = propertyType.getValueType()
            if hasattr(valueType, 'propertiesUpdated'):
                valueType.propertiesUpdated(propertyName, oldValue, newValue, self)


    def setReadOnly(self, value):
        self.readOnly = value

    def _sortKeyFunction(self):
        return lambda item: (self.propertyShowType(item), item.userProfileId, item.idx)

    def spanInfo(self):
        return self._spanInfo

    @property
    def propertyTypeList(self):
        return [propType for propType in self._rowDataList if propType and not isinstance(propType, basestring)]

    def _setAction(self, action, clientId, withPropertyValues, clientSex = None, clientAge = None):
        self.action = action
        self.clientId = clientId
        if self.action:
            if withPropertyValues:
                propertyTypeList = [prop.type() for prop in action.getPropertiesById().values()]
            else:
                actionType = action.getType()
                propertyTypeList = [propType for propType in actionType.getPropertiesById().values()
                                    if propType.applicable(clientSex, clientAge) and self.visible(propType)]
        else:
            propertyTypeList = []
        propertyTypeList.sort(key=self._sortKeyFunction())
        self._rowDataList = []
        self._spanInfo = []
        userProfileId = None
        for propType in propertyTypeList:
            if propType.userProfileId != userProfileId:
                userProfileId = propType.userProfileId
                userProfileName = forceStringEx(QtGui.qApp.db.translate('rbUserProfile', 'id', userProfileId, 'name'))
                if userProfileName:
                    row = len(self._rowDataList)
                    self._rowDataList.append(userProfileName)
                    self._spanInfo.append((row, 0, 1, self.columnCount()))
            self._rowDataList.append(propType)

        self.updateActionStatusTip()
        self.reset()

    def setAction(self, action, clientId, clientSex, clientAge):
        self._setAction(action, clientId, withPropertyValues = False, clientSex = clientSex, clientAge = clientAge)

    def setAction2(self, action, clientId):
        self._setAction(action, clientId, withPropertyValues = True, clientSex = None, clientAge = None)

    def updateActionStatusTip(self):
        if self.action:
            actionType = self.action.getType()
            self.actionStatusTip = actionType.code + ': ' + actionType.name
        else:
            self.actionStatusTip = None

    def visible(self, propertyType):
        # скрывать, если хотя бы одно условие не выполненено
        if self.propertyShowType(propertyType) == self.PropertyShowType.Hide:
            return False

        return self.visibilityFilter == self.visibleAll or \
               self.visibilityFilter == self.visibleInJobTicket and propertyType.visibleInJobTicket

    def columnCount(self, index = QtCore.QModelIndex()):
        return 5

    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._rowDataList)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.column[section])
        elif orientation == QtCore.Qt.Vertical and section in xrange(len(self._rowDataList)):
            propertyType = self._rowDataList[section]
            if isinstance(propertyType, basestring):
                if role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant('')
                elif role == QtCore.Qt.ToolTipRole:
                    return QtCore.QVariant(u'Профиль прав, установленный для свойств, отображаемых в строках ниже')
                elif role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.QVariant(QtCore.Qt.AlignCenter)
            else:
                if role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant(foldText(propertyType.name, [CActionPropertiesTableView.titleWidth]))
                elif role == QtCore.Qt.ToolTipRole:
                    result = propertyType.descr if forceStringEx(propertyType.descr) else propertyType.name
                    return QtCore.QVariant(result)
                elif role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.QVariant(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
                elif role == QtCore.Qt.ForegroundRole:
                    prop = self.action.getPropertyById(propertyType.id)
                    evaluation = prop.getEvaluation()
                    if evaluation:
                        return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                elif role == QtCore.Qt.FontRole:
                    prop = self.action.getPropertyById(propertyType.id)
                    evaluation = prop.getEvaluation()
                    if evaluation and abs(evaluation) == 2:
                        font = QtGui.QFont()
                        font.setBold(True)
                        return QtCore.QVariant(font)
        return QtCore.QVariant()

    def getPropertyType(self, row):
        propType = self._rowDataList[row]
        if isinstance(propType, basestring):
            return None
        return propType

    @classmethod
    def propertyShowType(cls, propertyType):
        if propertyType.userProfileId is not None:
            if not QtGui.qApp.userHasProfile(propertyType.userProfileId):
                    if propertyType.userProfileBehaviour == propertyType.UserProfileBehaviour.DisableEdit:
                        return cls.PropertyShowType.ReadOnly
                    else:
                        return cls.PropertyShowType.Hide
        return cls.PropertyShowType.Show

    def hasCommonPropertyChangingRight(self, row):
        propertyType = self._rowDataList[row]
        if isinstance(propertyType, basestring):
            return False

        if self.propertyShowType(propertyType) == self.PropertyShowType.ReadOnly:
            return False

        if propertyType.canChangeOnlyOwner == 0: # все могут редактировать свойство
            return True
        elif propertyType.canChangeOnlyOwner == 1 and self.action:
            setPersonId = forceRef(self.action.getRecord().value('setPerson_id'))
            return setPersonId == QtGui.qApp.userId
        #atronah: условие ниже не имеет смысла, так как функция все равно возврщает False по дефолту
        # elif propertyType.canChangeOnlyOwner == 2: # Никто не может редактировать свойство
        #     return False
        return False

    def flags(self, index):
        row = index.row()
        if isinstance(self._rowDataList[row], basestring):
            return QtCore.Qt.NoItemFlags

        if self.readOnly or (self.action and self.action.isLocked()):
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            if self.hasCommonPropertyChangingRight(row):
                column = index.column()
                if column == self.ciIsAssigned and self._rowDataList[row].isAssignable:
                    return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                elif column == self.ciValue:
                    propertyType = self._rowDataList[row]
                    prop = self.action.getPropertyById(propertyType.id)
                    if hasattr(prop.type().valueType, 'isObsolete') and prop.type().valueType.isObsolete and not (prop.type().typeName == u'Квота пациента' and QtGui.qApp.userHasRight(urModifyObsoleteQuotas)):
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
                elif column == self.ciEvaluation:
                    propertyType = self._rowDataList[row]
                    if propertyType.defaultEvaluation in [0, 1]:  # 0-не определять, 1-автомат
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    elif propertyType.defaultEvaluation in [2, 3]:  # 2-полуавтомат, 3-ручное
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getDefaultEvaluation(self, propertyType, property, index):
        if propertyType.defaultEvaluation in (1, 2):
            if propertyType.defaultEvaluation == 2:
                if not property.getEvaluation() is None:
                    return '%+d' % property.getEvaluation()
            value = unicode(property.getText())
            if bool(value):
                try:
                    value = float(value)
                except ValueError:
                    return ''
                norm = property.getNorm()
                parts = norm.split('-')
                if len(parts) == 2:
                    try:
                        bottom = float(parts[0].replace(',', '.'))
                        top    = float(parts[1].replace(',', '.'))
                    except ValueError:
                        return ''
                    if bottom > top:
                        return ''
                    if value < bottom:
                        evaluation = -1
                    elif value > top:
                        evaluation = 1
                    else:
                        evaluation = 0
                    index = self.index(index.row(), self.ciEvaluation)
                    self.setData(index, QtCore.QVariant(evaluation))
                    return '%+d'%evaluation
        return ''

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        propertyType = self._rowDataList[row]
        if isinstance(propertyType, basestring):
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(propertyType)
            elif role == QtCore.Qt.TextAlignmentRole:
                    return QtCore.QVariant(QtCore.Qt.AlignCenter)
            return QtCore.QVariant()

        prop = self.action.getPropertyById(propertyType.id)
        if role == QtCore.Qt.DisplayRole:
            if column == self.ciValue:
                return toVariant(prop.getText())
            elif column == self.ciUnit:
                return QtCore.QVariant(self.unitData.getNameById(prop.getUnitId()))
            elif column == self.ciNorm:
                return toVariant(prop.getNorm())
            elif column == self.ciEvaluation:
                evaluation = prop.getEvaluation()
                if evaluation is None:
                    s = self.getDefaultEvaluation(propertyType, prop, index)
                else:
                    s = ('%+d'%evaluation) if evaluation else '0'
                return toVariant(s)
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.CheckStateRole:
            if column == self.ciIsAssigned:
                if propertyType.isAssignable:
                    return toVariant(QtCore.Qt.Checked if prop.isAssigned() else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.EditRole:
            if column == self.ciIsAssigned:
                return toVariant(prop.getStatus())
            elif column == self.ciValue:
                return toVariant(prop.getValue())
            elif column == self.ciUnit:
                return toVariant(prop.getUnitId())
            elif column == self.ciNorm:
                return toVariant(prop.getNorm())
            elif column == self.ciEvaluation:
                return toVariant(prop.getEvaluation())
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        elif role == QtCore.Qt.DecorationRole:
            if column == self.ciValue:
                return toVariant(prop.getImage())
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.ForegroundRole:
            evaluation = prop.getEvaluation()
            if evaluation:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        elif role == QtCore.Qt.FontRole:
            evaluation = prop.getEvaluation()
            if evaluation and abs(evaluation) == 2:
                font = QtGui.QFont()
                font.setBold(True)
                return QtCore.QVariant(font)
        elif role == QtCore.Qt.ToolTipRole:
            if column == self.ciIsAssigned:
                if propertyType.isAssignable:
                    return toVariant(u'Назначено' if prop.isAssigned() else u'Не назначено')
        elif role == QtCore.Qt.StatusTipRole:
            if self.actionStatusTip:
                return toVariant(self.actionStatusTip)
        return QtCore.QVariant()

    def emitDataChanged(self):
        leftTop = self.index(0, 0)
        rightBottom = self.index(self.rowCount(), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), leftTop, rightBottom)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        column = index.column()
        propertyType = self._rowDataList[row]
        if isinstance(propertyType, basestring):
            return False

        prop = self.action.getPropertyById(propertyType.id)
        if role == QtCore.Qt.EditRole:
            if column == self.ciValue:
                if not propertyType.isVector:
                    old_value = prop.getValue()
                    new_value = propertyType.convertQVariantToPyValue(value)
                    if old_value == new_value:
                        return False
                    prop.setValue(propertyType.convertQVariantToPyValue(value))
                    self.dataChanged.emit(index, index)
                    self.getDefaultEvaluation(propertyType, prop, index)
                    self.propertyValueChanged.emit(propertyType.name, toVariant(old_value), toVariant(new_value))
                    if prop.isActionNameSpecifier():
                        self.action.updateSpecifiedName()
                        self.emit(QtCore.SIGNAL('actionNameChanged()'))
                    return True
                else:
                    old_value = prop.getValue()
                    new_value = [forceRef(x) for x in value]
                    if old_value == new_value:
                        return False
                    prop.setValue(new_value)
                    self.dataChanged.emit(index, index)
                    self.propertyValueChanged.emit(propertyType.name, toVariant(old_value), toVariant(new_value))
                    return True

            elif column == self.ciEvaluation:
                prop.setEvaluation(None if value.isNull() else forceInt(value))
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                return True
        elif role == QtCore.Qt.CheckStateRole:
            if column == self.ciIsAssigned:
                prop.setAssigned(forceInt(value) == QtCore.Qt.Checked)
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                return True
        return False

    def getProperty(self, row):
        propertyType = self._rowDataList[row]
        if isinstance(propertyType, basestring):
            return None
        return self.action.getPropertyById(propertyType.id)

    def setLaboratoryCalculatorData(self, data):
        propertyTypeIdList = [propType.id if not isinstance(propType, basestring) else None for propType in self._rowDataList ]
        for sValuePair in data.split(';'):
            sValuePair = forceStringEx(sValuePair).strip('()').split(',')
            propertyTypeId, value = forceInt(sValuePair[0]), sValuePair[1]
            if propertyTypeId in propertyTypeIdList:
                propertyTypeIndex = propertyTypeIdList.index(propertyTypeId)
                propertyType = self._rowDataList[propertyTypeIndex]
                prop = self.action.getPropertyById(propertyTypeId)
                prop.setValue(propertyType.convertQVariantToPyValue(QtCore.QVariant(value)))
        begIndex = self.index(0, 0)
        endIndex = self.index(self.rowCount()-1, self.columnCount()-1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), begIndex, endIndex)

    def setPlannedEndDateByJobTicket(self, jobTicketId):
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')
        tableJobType = db.table('rbJobType')

        table = tableJobTicket.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
        table = table.leftJoin(tableJobType, tableJobType['id'].eq(tableJob['jobType_id']))
        cols = [
            tableJobTicket['datetime'].alias('datetime'),
            tableJobType['ticketDuration'].alias('duration')
        ]
        rec = db.getRecordEx(table, cols, tableJobTicket['id'].eq(jobTicketId))
        if rec:
            date = forceDate(rec.value('datetime'))
            duration = forceInt(rec.value('duration'))
            self.emit(QtCore.SIGNAL('setCurrentActionEndDate(QDate)'), date.addDays(duration))

    def plannedEndDateByJobTicket(self):
        actionType = self.action.getType()
        return actionType.defaultPlannedEndDate == 3


class CExActionPropertiesTableModel(CActionPropertiesTableModel):
    def _sortKeyFunction(self):
        return lambda item: (
            not self.action.getPropertyById(item.id).isAssigned(), self.propertyShowType(item), item.isFrozen, item.userProfileId, item.idx)

    def countFrozen(self):
        count = 0
        for value in self.propertyTypeList:
            if value.isFrozen:
                count += 1
        return count


class CActionPropertyBaseDelegate(QtGui.QItemDelegate):
    def __init__(self, lineHeight, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.lineHeight = lineHeight

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter] and isinstance(editor, QtGui.QTextEdit):
                return False
        return QtGui.QItemDelegate.eventFilter(self, editor, event)

    def commit(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, QtGui.QAbstractItemDelegate.NoHint)


class CActionPropertyDelegate(CActionPropertyBaseDelegate):
    def __init__(self, lineHeight, parent):
        CActionPropertyBaseDelegate.__init__(self, lineHeight, parent)

    def paint(self, painter, option, index):
        model = index.model()
        row = index.row()
        propertyType = model.getPropertyType(row)
        if propertyType and propertyType.isHtml():
            if option.state & QtGui.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
            painter.setBrush(QtGui.QColor(QtCore.Qt.black))
            document = QtGui.QTextDocument()
            document.setHtml(index.data(QtCore.Qt.DisplayRole).toString())
            context = QtGui.QAbstractTextDocumentLayout.PaintContext()
            context.palette = option.palette
            if option.state & QtGui.QStyle.State_Selected:
                context.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
            else:
                context.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
            painter.save()
            layout = document.documentLayout()
            painter.setClipRect(option.rect, QtCore.Qt.IntersectClip)
            painter.translate(option.rect.x(), option.rect.y())
            layout.draw(painter, context)
            painter.restore()
        else:
            CActionPropertyBaseDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        model = index.model()
        row = index.row()
        propertyType = model.getPropertyType(row)
        editor = propertyType.createEditor(model.action, parent, model.clientId)
        editor.setStatusTip(forceString(model.data(index, QtCore.Qt.StatusTipRole)))
        self.connect(editor, QtCore.SIGNAL('commit()'), self.commit)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        prop = model.getProperty(index.row())
        if prop:
            if isinstance(editor, (CRLSExtendedActionPropertyValueType.ScalarEditor,
                                   CRLSExtendedActionPropertyValueType.VectorEditor)):
                editor.setValue(prop._value)
                return
            id = forceString(value)
            if id and prop.type().tableName in (u'ActionProperty_Job_Ticket'):
                status = forceString(QtGui.qApp.db.translate('Job_Ticket', 'id', id, 'status'))
                if status == '2':
                    editor.setEnabled(False)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model = index.model()
        value = editor.value()

        if isinstance(editor, (CRLSExtendedActionPropertyValueType.ScalarEditor,
                               CRLSExtendedActionPropertyValueType.VectorEditor)):
            model.setData(index, value)
        elif isinstance(value, list):
            model.setData(index, [toVariant(x) for x in value])
        else:
            model.setData(index, toVariant(value))
        if type(editor) == CJobTicketActionPropertyValueType.CPropEditor and model.plannedEndDateByJobTicket and type(value) != list:
            model.setPlannedEndDateByJobTicket(value)

    def sizeHint(self, option, index):
        model = index.model()
        row = index.row()
        propertyType = model.getPropertyType(row)
        if propertyType is None:
            return super(CActionPropertyDelegate, self).sizeHint(option, index)
        prop = model.action.getPropertyById(propertyType.id)
        prefferedHeightUnit, prefferedHeight = prop.getPrefferedHeight()
        result = QtCore.QSize(10, self.lineHeight*prefferedHeight if prefferedHeightUnit == 1 else prefferedHeight)
        return result


class CActionPropertyEvaluationDelegate(CActionPropertyBaseDelegate):
    def __init__(self, lineHeight, parent=None):
        CActionPropertyBaseDelegate.__init__(self, lineHeight, parent)

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        editor.addItem('', QtCore.QVariant())
        editor.addItem(u'-2', QtCore.QVariant(-2))
        editor.addItem(u'-1', QtCore.QVariant(-1))
        editor.addItem(u'0', QtCore.QVariant(0))
        editor.addItem(u'+1', QtCore.QVariant(+1))
        editor.addItem(u'+2', QtCore.QVariant(+2))
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        index = 0 if value.isNull() else forceInt(value)+3
        editor.setCurrentIndex(index)

    def setModelData(self, editor, model, index):
        model = index.model()
        model.setData(index, editor.itemData(editor.currentIndex()))

    def sizeHint(self, option, index):
        return QtCore.QSize(10, self.lineHeight)


class CActionPropertiestableVerticalHeaderView(QtGui.QHeaderView):
    def __init__(self, orientation, parent=None):
        QtGui.QHeaderView.__init__(self, orientation, parent)

    def sectionSizeFromContents(self, logicalIndex):
        model = self.model()
        if model and logicalIndex in xrange(model.rowCount()):
            orientation = self.orientation()
            opt = QtGui.QStyleOptionHeader()
            self.initStyleOption(opt)
            var = model.headerData(logicalIndex, orientation, QtCore.Qt.FontRole)
            if var and var.isValid() and var.type() == QtCore.QVariant.Font:
                fnt = var.toPyObject()
            else:
                fnt = self.font()
            opt.fontMetrics = QtGui.QFontMetrics(fnt)
            sizeText = QtCore.QSize(4,4)
            opt.text = model.headerData(logicalIndex, orientation, QtCore.Qt.DisplayRole).toString()
            sizeText = self.style().sizeFromContents(QtGui.QStyle.CT_HeaderSection, opt, sizeText, self)
            sizeFiller = QtCore.QSize(4,4)
            opt.text = QtCore.QString('x'*CActionPropertiesTableView.titleWidth)
            sizeFiller = self.style().sizeFromContents(QtGui.QStyle.CT_HeaderSection, opt, sizeFiller, self)
            return QtCore.QSize(max(sizeText.width(), sizeFiller.width()),
                                max(sizeText.height(), sizeFiller.height()))
        else:
            return QtGui.QHeaderView.sectionSizeFromContents(self, logicalIndex)


class CActionPropertiesTableDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        model = index.model()
        column = index.column()
        if column == model.ciUnit:
            option.text = u''
            self.parent().style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter)
            painter.save()
            doc = QtGui.QTextDocument(self)
            doc.setHtml(model.data(index, QtCore.Qt.DisplayRole).toString())
            painter.translate(option.rect.left(), option.rect.top())
            clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
            doc.drawContents(painter, clip)
            painter.restore()
        else:
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        model = index.model()
        column = index.column()
        if column == model.ciUnit:
            doc = QtGui.QTextDocument(self)
            doc.setHtml(model.data(index).toString())
            size = doc.size()
        else:
            size = QtGui.QStyledItemDelegate.sizeHint(self, option, index)
        return QtCore.QSize(int(size.width()), int(size.height()))


class CActionPropertiesTableView(CExtendedTableView, CPreferencesMixin):
    titleWidth = 20

    def __init__(self, parent):
        super(CActionPropertiesTableView, self).__init__(parent)
        self._verticalHeader = CActionPropertiestableVerticalHeaderView(QtCore.Qt.Vertical, self)
        self.setVerticalHeader(self._verticalHeader)
        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3*h/2)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.valueDelegate = CActionPropertyDelegate(self.fontMetrics().height(), self)
        self.setItemDelegateForColumn(CActionPropertiesTableModel.ciValue, self.valueDelegate)
        self.evaluationDelegate = CActionPropertyEvaluationDelegate(self.fontMetrics().height(), self)
        self.setItemDelegateForColumn(CActionPropertiesTableModel.ciEvaluation, self.evaluationDelegate)
        self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self._popupMenu = None
        self._actCopyCell = None
        self.setItemDelegate(CActionPropertiesTableDelegate(self))

    def getHeightFactor(self, row):
        propertyTypeList = self.model().propertyTypeList
        if 0 <= row < len(propertyTypeList):
            heightFactor = propertyTypeList[row].redactorSizeFactor
            if heightFactor < 0:
                heightFactor = abs(heightFactor)
                return 1.0/heightFactor
            elif heightFactor > 0:
                return heightFactor
        return 1

    def sizeHintForRow(self, row):
        model = self.model()
        if model:
            index = model.index(row, CActionPropertiesTableModel.ciValue)
            heightFactor = self.getHeightFactor(row)
            return max(self.valueDelegate.sizeHint(QtGui.QStyleOptionViewItem(), index).height(),
                       self.evaluationDelegate.sizeHint(QtGui.QStyleOptionViewItem(), index).height()
                      )*heightFactor+1
        else:
            return -1

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        for action in actions:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        return self._popupMenu

    def popupMenu(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        return self._popupMenu

    def addPopupSeparator(self):
        self.popupMenu().addSeparator()

    def addPopupAction(self, action):
        self.popupMenu().addAction(action)

    def addPopupCopyCell(self):
        self._actCopyCell = QtGui.QAction(u'Копировать', self)
        self._actCopyCell.setObjectName('actCopyCell')
        self.connect(self._actCopyCell, QtCore.SIGNAL('triggered()'), self.copyCurrentCell)
        self.addPopupAction(self._actCopyCell)

    def focusInEvent(self, event):
        super(CActionPropertiesTableView, self).focusInEvent(event)
        self.updateStatusTip(self.currentIndex())

    def focusOutEvent(self, event):
        self.updateStatusTip(None)
        super(CActionPropertiesTableView, self).focusOutEvent(event)

    def updateStatusTip(self, index):
        tip = forceString(index.data(QtCore.Qt.StatusTipRole)) if index else ''
        event = QtGui.QStatusTipEvent(tip)
        self.setStatusTip(tip)
        QtGui.qApp.sendEvent(self.parent(), event)

    def moveCursor(self, cursorAction, modifiers):
        if cursorAction in [QtGui.QAbstractItemView.MoveNext, QtGui.QAbstractItemView.MoveRight]:
            return super(CActionPropertiesTableView, self).moveCursor(QtGui.QAbstractItemView.MoveDown, modifiers)
        elif cursorAction in [QtGui.QAbstractItemView.MovePrevious, QtGui.QAbstractItemView.MoveLeft]:
            return super(CActionPropertiesTableView, self).moveCursor(QtGui.QAbstractItemView.MoveUp, modifiers)
        else:
            return super(CActionPropertiesTableView, self).moveCursor(QtGui.QAbstractItemView.CursorAction(cursorAction), modifiers)

    def contextMenuEvent(self, event): # event: QContextMenuEvent
        if self._popupMenu:
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()

    def popupMenuAboutToShow(self):
        currentIndex = self.currentIndex()
        curentIndexIsValid = currentIndex.isValid()
        if self._actCopyCell:
            self._actCopyCell.setEnabled(curentIndexIsValid)

    def copyCurrentCell(self):
        index = self.currentIndex()
        if index.isValid():
            carrier = QtCore.QMimeData()
            dataAsText = self.model().data(index, QtCore.Qt.DisplayRole)
            carrier.setText(dataAsText.toString() if dataAsText else '' )
            QtGui.qApp.clipboard().setMimeData(carrier)

    def showHistory(self):
        index = self.currentIndex()
        model = self.model()
        row = index.row()
        if 0<=row<model.rowCount():
            actionProperty = model.getProperty(row)
            dlg = CPropertyHistoryDialog(model.clientId, [(actionProperty, True, True)], self)
            dlg.exec_()

    def showHistoryEx(self):
        index = self.currentIndex()
        model = self.model()
        row = index.row()
        if 0<=row<model.rowCount():
            dlgChooser = CActionPropertyChooser(self, self.model().propertyTypeList)
            if dlgChooser.exec_():
                propertyTypeList = dlgChooser.getSelectedPropertyTypeList()
                if propertyTypeList:
                    dlg = CPropertyHistoryDialog(model.clientId, [(model.action.getProperty(propertyType.name), showUnit, showNorm) for propertyType, showUnit, showNorm in propertyTypeList], self)
                    dlg.exec_()

    def colKey(self, col):
        return unicode('width '+forceString(col.title()))

    def loadPreferences(self, preferences):
        model = self.model()
        nullSizeDetected = False
        if model:
            for i in xrange(model.columnCount()):
                width = forceInt(getPref(preferences, 'col_%d'%i, None))
                if width:
                    self.setColumnWidth(i, width)
                else:
                    if not self.isColumnHidden(i):
                        nullSizeDetected = True
        if nullSizeDetected:
            self.resizeColumnsToContents()
            width = self.columnWidth(0)
            self.setColumnWidth(0, width/2) # назначено
            self.setColumnWidth(1, self.columnWidth(1)+self.columnWidth(4)) # значение
            self.setColumnWidth(4, width/2) # оценка

    def savePreferences(self):
        preferences = {}
        model = self.model()
        if model:
            for i in xrange(model.columnCount()):
                width = self.columnWidth(i)
                setPref(preferences, 'col_%d'%i, QtCore.QVariant(width))
        return preferences


class CExActionPropertiesTableView(CActionPropertiesTableView):
    def __init__(self, parent):
        CActionPropertiesTableView.__init__(self, parent)
        self.frozenTableView = CFrozenActionPropertiesTableView(self)
        self.countFrozen = 0
        self.connect(self.horizontalHeader(), QtCore.SIGNAL('sectionResized(int, int, int)'), self.updateSectionWidth)
        self.connect(self.verticalHeader(), QtCore.SIGNAL('sectionResized(int, int, int)'), self.updateSectionHeight)
        self.connect(self.frozenTableView.verticalHeader(), QtCore.SIGNAL('sectionResized(int,int,int)'), self.updateFrozenSectionHeight)
        self.connect(self.frozenTableView.horizontalScrollBar(), QtCore.SIGNAL('valueChanged(int)'), self.horizontalScrollBar().setValue)
        self.connect(self.horizontalScrollBar(), QtCore.SIGNAL('valueChanged(int)'), self.frozenTableView.horizontalScrollBar().setValue)
        self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        
    def setSelectionModelEx(self, selectionModel):
        self.frozenTableView.setSelectionModel(selectionModel)
        self.setSelectionModel(selectionModel)

    def setModelEx(self, model):
        self.setModel(model)
        self.frozenTableView.setModel(model)

    def init(self):
        self.frozenTableView.selectRow(0)
        self.frozenTableView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.frozenTableView.horizontalHeader().hide()

        self.countFrozen = self.model().countFrozen()
        self.setStyleSheet('CExActionPropertiesTableView {border: none}')
        if self.countFrozen:
            self.viewport().stackUnder(self.frozenTableView)
            for row in range(self.countFrozen, self.model().rowCount()):
                self.frozenTableView.setRowHidden(row, True)

            for row in range(self.countFrozen):
                self.frozenTableView.setRowHeight(row, self.rowHeight(row))
            self.frozenTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.frozenTableView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

            self.frozenTableView.show()

        self.setCurrentIndex(QtCore.QModelIndex())
        self.updateFrozenTableGeometry()

    def updateSectionWidth(self, logicalIndex, o , newSize):
        self.frozenTableView.setColumnWidth(logicalIndex, newSize)

    def updateSectionHeight(self, logicalIndex, o, newSize):
        if logicalIndex in range(self.countFrozen):
            self.frozenTableView.setRowHeight(logicalIndex, newSize)
            self.updateFrozenTableGeometry()

    def updateFrozenSectionHeight(self, logicalIndex, o, newSize):
        if logicalIndex in range(self.countFrozen):
            self.setRowHeight(logicalIndex, newSize)
            self.updateFrozenTableGeometry()

    def resizeEvent(self, event):
        CActionPropertiesTableView.resizeEvent(self, event)
        self.updateFrozenTableGeometry()

    def moveCursor(self, cursorAction, modifiers):
        current = CActionPropertiesTableView.moveCursor(self, cursorAction, modifiers)
        frozenHeight = 0
        for row in range(self.countFrozen):
            frozenHeight += self.frozenTableView.rowHeight(self.countFrozen)
        if cursorAction in (self.MoveUp, self.MoveNext) and current.row()>self.countFrozen and self.visualRect(current).topLeft().y() < frozenHeight:
            newValue = self.verticalScrollBar().value() + self.visualRect(current).topLeft().y() - frozenHeight
            self.verticalScrollBar().setValue(newValue)
        return current

    def updateFrozenTableGeometry(self):
        frozenHeight = 0
        for row in range(self.countFrozen):
            frozenHeight += self.rowHeight(row)
        self.frozenTableView.setGeometry(self.frameWidth()*2, self.horizontalHeader().height() + self.frameWidth()*2, self.viewport().width() + self.verticalHeader().width(), frozenHeight)

    def setColumnHidden(self, column, hide):
        CActionPropertiesTableView.setColumnHidden(self, column, hide)
        self.frozenTableView.setColumnHidden(column, hide)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def currentChanged(self, current, previous):
        if current.row()<self.countFrozen:
            self.frozenTableView.currentChanged(current, previous)
        else:
            CActionPropertiesTableView.currentChanged(self, current, previous)


class CFrozenActionPropertiesTableView(CActionPropertiesTableView):
    def __init__(self, parent):
        CActionPropertiesTableView.__init__(self, parent)

    def wheelEvent(self, event):
        self.parent().wheelEvent(event)
        event.ignore()
