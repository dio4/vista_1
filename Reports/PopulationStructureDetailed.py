# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui

from KLADR.KLADRModel import getStreetName
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_PopulationStructureDetailedSetup import Ui_PopulationStructureDetailedSetup
from library.ItemsListModel import CItemsListModel
from library.Utils import forceInt, forceString
from library.crbcombobox import CRBComboBox

STMT = '''
SELECT
  ah.KLADRStreetCode as street,
  CONCAT(ah.number, IF(ah.corpus, CONCAT('к', ah.corpus), '')) as house,
  a.flat as flat,
  CONCAT_WS(' ', c.lastName, c.firstName, c.patrName) as name,
  YEAR(c.birthDate) as birthYear,
  GROUP_CONCAT(DISTINCT css.begDate SEPARATOR ', ') as monitoringStart,
  GROUP_CONCAT(DISTINCT d.MKB SEPARATOR ', ') as diagnosis
FROM
  Client c
  INNER JOIN ClientAddress ca ON c.id = ca.client_id AND ca.deleted='0'
  INNER JOIN Address a ON ca.address_id = a.id AND a.deleted='0'
  INNER JOIN AddressHouse ah ON a.house_id = ah.id AND ah.deleted='0'
  INNER JOIN OrgStructure_Address osa ON ah.id = osa.house_id
  LEFT JOIN ClientSocStatus css ON c.id = css.client_id AND css.deleted='0'
  LEFT JOIN Diagnosis d ON c.id = d.client_id AND d.deleted='0'
WHERE {where}
GROUP BY c.id
ORDER BY street, LPAD(LOWER(house), 10, 0), LPAD(LOWER(flat), 10, 0), name
'''


def select_data(date, age_start, age_end, soc_class, soc_type, org_structure, address_street, address_house):
    db = QtGui.qApp.db
    cond = [
        'c.birthDate BETWEEN \'%s\' AND \'%s\'' % (
            date.addYears(-age_end-1).toString('yyyy-MM-dd'),
            date.addYears(-age_start).toString('yyyy-MM-dd')
        )]
    if soc_type:
        cond.append('css.socStatusType_id=%d' % soc_type)
    elif soc_class:
        cond.append('css.socStatusClass_id=%d' % soc_class)

    if org_structure:
        cond.append('osa.master_id IN (\'%s\')' %
                    '\', \''.join((str(x) for x in getOrgStructureDescendants(org_structure))))
    else:
        cond.append('osa.master_id IN (\'%s\')' %
                    '\', \''.join(str(getOrgStructureDescendants(QtGui.qApp.currentOrgStructureId()))))

    if address_house:
        cond.append('ah.id = \'%d\'' % address_house)
    elif address_street:
        cond.append('ah.KLADRStreetCode = \'%s\'' % address_street)

    stmt = STMT.format(where=db.joinAnd(cond))
    return db.query(stmt)


class CPopulationStructureDetailed(CReport):
    def __init__(self, parent):
        super(CPopulationStructureDetailed, self).__init__(parent)
        self.setTitle(u'Состав населения по участкам (детализированный)')

    def getSetupDialog(self, parent):
        result = CPopulationStructureDetailedSetupDialog(parent)
        return result

    def build(self, params):
        date = params['date']
        age_start = params['ageFrom']
        age_end = params['ageTo']
        soc_class = params['socStatusClassId']
        soc_type = params['socStatusTypeId']
        org_structure = params['orgStructureId']
        address_street = params['addressStreet']
        address_house = params['addressHouse']

        query = select_data(date, age_start, age_end, soc_class, soc_type, org_structure, address_street, address_house)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        columns = (
            ('%30', [u'Улица'], CReportBase.AlignLeft),
            ('%30', [u'Дом'], CReportBase.AlignLeft),
            ('%30', [u'Квартира'], CReportBase.AlignLeft),
            ('%30', [u'Ф.И.О.'], CReportBase.AlignLeft),
            ('%30', [u'Год рождения'], CReportBase.AlignLeft),
            ('%30', [u'Дата постановки на учет'], CReportBase.AlignLeft),
            ('%30', [u'Диагноз'], CReportBase.AlignLeft),
        )

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        table = createTable(cursor, columns)

        last = {
            'street': '',
            'street_row': 1,
            'house': '',
            'house_row': 1,
            'flat': '',
            'flat_row': 1,
        }

        def merge_flat(row):
            table.mergeCells(last['flat_row'], 2, (row - last['flat_row']), 1)

        def merge_house(row):
            table.mergeCells(last['house_row'], 1, (row - last['house_row']), 1)
            merge_flat(row)
            last['flat'] = ''
            last['flat_row'] = row

        def merge_street(row):
            table.mergeCells(last['street_row'], 0, (row - last['street_row']), 1)
            merge_house(row)
            last['house'] = ''
            last['house_row'] = row

        while query.next():
            rec = query.record()
            i = table.addRow()

            street = forceString(rec.value('street'))
            if street != last['street']:
                merge_street(i)
                table.setText(i, 0, getStreetName(street))
                last['street'] = street
                last['street_row'] = i

            house = forceString(rec.value('house'))
            if house != last['house']:
                merge_house(i)
                table.setText(i, 1, house)
                last['house'] = house
                last['house_row'] = i

            flat = forceString(rec.value('flat'))
            if flat != last['flat']:
                merge_flat(i)
                table.setText(i, 2, flat)
                last['flat'] = flat
                last['flat_row'] = i

            table.setText(i, 3, forceString(rec.value('name')))
            table.setText(i, 4, forceString(rec.value('birthYear')))
            table.setText(i, 5, forceString(rec.value('monitoringStart')))
            table.setText(i, 6, forceString(rec.value('diagnosis')))

        merge_street(table.rows())

        return doc


class CPopulationStructureDetailedSetupDialog(QtGui.QDialog, Ui_PopulationStructureDetailedSetup):
    def __init__(self, parent):
        super(CPopulationStructureDetailedSetupDialog, self).__init__(parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)

        self.lstStreet.setModel(CStreetModel(self))
        self.lstHouse.setModel(CHouseModel(self))

    def setParams(self, params):
        self.edtDate.setDate(params.get('date', QtCore.QDate().currentDate()))
        self.edtAgeStart.setValue(params.get('ageFrom', 0))
        self.edtAgeEnd.setValue(params.get('ageTo', 150))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))

    def params(self):
        street_idx = self.lstStreet.currentIndex()
        house_idx = self.lstHouse.currentIndex()
        return {
            'date': self.edtDate.date(),
            'ageFrom': self.edtAgeStart.value(),
            'ageTo': self.edtAgeEnd.value(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'socStatusClassId': self.cmbSocStatusClass.value(),
            'socStatusTypeId': self.cmbSocStatusType.value(),
            'addressStreet': self.lstStreet.model().value(street_idx),
            'addressHouse': self.lstHouse.model().value(house_idx),
        }

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        class_id = self.cmbSocStatusClass.value()
        soc_filter = ('class_id = %d' % class_id) if class_id else ''
        self.cmbSocStatusType.setFilter(soc_filter)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        if self.lstStreet.model():
            self.lstStreet.model().setOrgStructure(orgStructureId)
            self.lstStreet.setCurrentIndex(self.lstStreet.model().first())

            self.lstHouse.model().setOrgStructure(orgStructureId)
            self.lstHouse.model().setStreet(None)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_lstStreet_clicked(self, index):
        self.lstHouse.model().setStreet(index.internalPointer())
        self.lstHouse.setCurrentIndex(self.lstHouse.model().first())


class CStreetModel(CItemsListModel):
    def __init__(self, parent):
        super(CStreetModel, self).__init__(parent)
        self._orgStructure = None
        self._db = QtGui.qApp.db
        self._tbl_osa = self._db.table('OrgStructure_Address')
        self._tbl_ah = self._db.table('AddressHouse')
        self._tbl = self._tbl_osa.innerJoin(self._tbl_ah, self._tbl_osa['house_id'].eq(self._tbl_ah['id']))

    def setOrgStructure(self, value):
        self._orgStructure = value
        self.reset()

    def orgStructure(self):
        return self._orgStructure

    def loadItems(self):
        items = []
        if self._orgStructure:
            items.append((None, u'<все>'))
            osList = getOrgStructureDescendants(self._orgStructure)
            for item in self._db.getRecordList(self._tbl,
                                               (self._tbl_ah['KLADRStreetCode'],),
                                               self._tbl_osa['master_id'].inlist(osList),
                                               self._tbl_ah['KLADRStreetCode'],
                                               True):
                items.append((
                    forceString(item.value('KLADRStreetCode')),
                    getStreetName(forceString(item.value('KLADRStreetCode'))) or u'<пусто>'
                ))
        return items


class CHouseModel(CItemsListModel):
    def __init__(self, parent):
        super(CHouseModel, self).__init__(parent)
        self._orgStructure = None
        self._street = None
        self._db = QtGui.qApp.db
        self._tbl_osa = self._db.table('OrgStructure_Address')
        self._tbl_ah = self._db.table('AddressHouse')
        self._tbl = self._tbl_osa.innerJoin(self._tbl_ah, self._tbl_osa['house_id'].eq(self._tbl_ah['id']))

    def setOrgStructure(self, value):
        self._orgStructure = value
        self.reset()

    def orgStructure(self):
        return self._orgStructure

    def setStreet(self, value):
        self._street = value
        self.reset()

    def street(self):
        return self._street

    def loadItems(self):
        items = []
        if self._orgStructure and self._street is not None:
            items.append((None, u'<все>'))
            osList = getOrgStructureDescendants(self._orgStructure)
            for item in self._db.getRecordList(self._tbl,
                                               (self._tbl_ah['id'], self._tbl_ah['number'], self._tbl_ah['corpus']),
                                               self._db.joinAnd((
                                                       self._tbl_osa['master_id'].inlist(osList),
                                                       self._tbl_ah['KLADRStreetCode'].eq(self._street)
                                               ))):
                number = forceString(item.value('number'))
                corpus = forceString(item.value('corpus'))
                items.append((
                    forceInt(item.value('id')),
                    (number + ((u'к' + corpus) if corpus else '')) or u'<пусто>'
                ))
        return items
