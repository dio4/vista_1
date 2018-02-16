# coding=utf-8
import xml.etree.ElementTree
from PyQt4 import QtCore, QtGui, QtSql

import re
import requests

import library.database
from library import xlwt
from Ui_ImportDKKBPersons import Ui_ImportDKKBPersonsDialog
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceString, getPref, forceDate, forceBool
from os import path


def parse_card_employee(el):
    def get_attr(tag, attr=None):
        elem = el.find('{http://www.dkkb.org/1c/Employees}' + tag)
        if elem is not None:
            if attr:
                if attr in elem.attrib:
                    return elem.attrib[attr]
                else:
                    return None
            else:
                return elem.text
        else:
            return None

    out = {
        'GUID': el.attrib['GUID'],
        'TabNumber': el.attrib['TabNumber'],
        'Surname': get_attr('Surname') or '',
        'Name': get_attr('Name') or '',
        'Patroname': get_attr('Patroname') or '',
        'DateBirth': get_attr('DateBirth'),
        'Sex': get_attr('Sex'),
        'SNILS': get_attr('SNILS'),
        'DateBegin': get_attr('DateBegin'),
        'DateEnd': get_attr('DateEnd'),
        'Subdivision': get_attr('Subdivision'),
        'SubdivisionGUID': get_attr('Subdivision', 'GUID') or '',
        'Post': get_attr('Post'),
        'PostGUID': get_attr('Post', 'GUID') or '',
        'Speciality': get_attr('Speciality'),
        'SpecialityGUID': get_attr('Speciality', 'GUID') or '',
    }

    if out['SNILS']:
        out['SNILS'] = out['SNILS'].replace(' ', '').replace('-', '')
    if out['TabNumber']:
        out['TabNumber'] = unicode(int(out['TabNumber']))

    if not out['Sex']:
        out['Sex'] = 0
    elif out['Sex'].startswith(u'Муж'):
        out['Sex'] = 1
    elif out['Sex'].startswith(u'Жен'):
        out['Sex'] = 2
    else:
        out['Sex'] = 0

    return out


def parse_soap_answer(answer, func):
    root = xml.etree.ElementTree.fromstring(answer)
    root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
    root = root.find('{http://www.dkkb.org/1c/Employees}%sResponse' % func)
    root = root.find('{http://www.dkkb.org/1c/Employees}return')
    employees = xml.etree.ElementTree.fromstring(root.text.encode('utf-8'))
    return [parse_card_employee(emp) for emp in employees]


class Worker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int, int, unicode)  # total, value, message
    done = QtCore.pyqtSignal(dict)
    error = QtCore.pyqtSignal(unicode)

    REQUEST_SKELETON = u'''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:emp="http://www.dkkb.org/1c/Employees">
                               <x:Header/>
                               <x:Body>
                                   <emp:{method}>
                                      {attributes}
                                   </emp:{method}>
                               </x:Body>
                           </x:Envelope>'''

    RETIRE_CHECK_QUERY = u'''SELECT
                                  p.id AS id, po.type AS type, po.date AS date
                              FROM
                                  Person p
                                  INNER JOIN
                                      (SELECT
                                          po1.*
                                      FROM
                                          Person_Order po1
                                      LEFT JOIN Person_Order po2 ON po1.master_id = po2.master_id
                                          AND po1.date < po2.date
                                      WHERE
                                          po2.id IS NULL) po ON (p.id = po.master_id)'''

    ORDER_INSERT_QUERY = u'INSERT INTO Person_Order (`date`, `documentDate`, `master_id`, `type`, `documentType_id`,' \
                         u'                                                           `orgStructure_id`, `post_id`) ' \
                         u'VALUES (\'{date}\', \'{date}\', \'{person_id}\', \'{type}\', \'{doc_type}\', ' \
                         u'                                                             \'{os_id}\', \'{post_id}\')'
    ORDER_BEGIN = 0
    ORDER_RETIRE = 1

    def __init__(self, parent):
        super(Worker, self).__init__(parent)
        self.url = ''
        self.login = ''
        self.password = ''
        self.sync = False
        self.sync_date = ''
        self.retire = False
        self.retire_start = ''
        self.retire_end = ''

        self.abort = None
        self.stats = None
        self.reset()

        self.org_structures = dict()
        self.posts = dict()
        self.specialities = dict()
        self.retire_docs = -1
        self.begin_docs = -1

        self.db = QtGui.qApp.db  # type: library.database.CMySqlDatabase
        self.person_tbl = self.db.table('Person')
        self.tbl = self.person_tbl
        self.os_tbl = self.db.table('OrgStructure')
        self.tbl = self.tbl.leftJoin(self.os_tbl, self.person_tbl['orgStructure_id'].eq(self.os_tbl['id']))
        self.post_tbl = self.db.table('rbPost')
        self.tbl = self.tbl.leftJoin(self.post_tbl, self.person_tbl['post_id'].eq(self.post_tbl['id']))
        self.spec_tbl = self.db.table('rbSpeciality')
        self.tbl = self.tbl.leftJoin(self.spec_tbl, self.person_tbl['speciality_id'].eq(self.spec_tbl['id']))

        self.order_tbl = self.db.table('Person_Order')
        self.docs_tbl = self.db.table('rbDocumentType')

        self.cols = (
            self.person_tbl['id'].alias('id'),
            self.person_tbl['code'].alias('code'),
            self.person_tbl['firstName'].alias('firstName'),
            self.person_tbl['lastName'].alias('lastName'),
            self.person_tbl['patrName'].alias('patrName'),
            self.person_tbl['birthDate'].alias('birthDate'),
            self.person_tbl['sex'].alias('sex'),
            self.person_tbl['SNILS'].alias('SNILS'),
            self.person_tbl['retired'].alias('retired'),
            self.person_tbl['retireDate'].alias('retireDate'),
            self.person_tbl['syncGUID'].alias('personGUID'),
            self.os_tbl['syncGUID'].alias('osGUID'),
            self.post_tbl['syncGUID'].alias('postGUID'),
            self.spec_tbl['syncGUID'].alias('specGUID'),
        )

    def reset(self):
        self.stats = {
            'created': dict(),
            'modified': dict(),
            'retired': dict(),
            'assigned': dict(),
        }
        self.abort = False

    def set_credentials(self, url, login, password, sync, sync_date, retire, retire_start, retire_end):
        self.url = url
        self.login = login
        self.password = password
        self.sync = sync
        self.sync_date = sync_date
        self.retire = retire
        self.retire_start = retire_start
        self.retire_end = retire_end

    def prepare_request(self, method, **kwargs):
        attrs = ''
        for key in kwargs:
            attrs += u'<emp:{key}>{value}</emp:{key}>\n'.format(key=key, value=kwargs[key])
        return self.REQUEST_SKELETON.format(method=method, attributes=attrs)

    def get_person(self, person):
        info_tuple = (person['Subdivision'], person['Post'], person['Speciality'])
        rec = self.db.getRecordEx(self.tbl, self.cols, self.person_tbl['syncGUID'].eq(person['GUID']))
        if not rec:
            cond = [self.person_tbl['code'].eq(person['TabNumber'])]

            if not person['SubdivisionGUID']:
                self.error.emit(u'В пришедших данных отсутствует GUID подразделения')
                cond.append(self.os_tbl['syncGUID'].isNull())
            else:
                cond.append(self.os_tbl['syncGUID'].like('%' + person['SubdivisionGUID'] + '%'))

            if not person['PostGUID']:
                self.error.emit(u'В пришедших данных отсутствует GUID должности')
                cond.append(self.post_tbl['syncGUID'].isNull())
            else:
                cond.append(self.post_tbl['syncGUID'].like('%' + person['PostGUID'] + '%'))

            if not person['SpecialityGUID']:
                self.error.emit(u'В пришедших данных отсутствует GUID специальности')
                cond.append(self.spec_tbl['syncGUID'].isNull())
            else:
                cond.append(self.spec_tbl['syncGUID'].like('%' + person['SpecialityGUID'] + '%'))

            rec = self.db.getRecordEx(self.tbl, self.cols, cond)
            if rec:
                person_id = forceInt(rec.value('id'))
                rec = self.db.getRecord(self.person_tbl, ('id', 'syncGUID'), person_id)
                rec.setValue('syncGUID', person['GUID'])
                self.db.updateRecord(self.person_tbl, rec)

                self.stats['assigned'][person_id] = info_tuple

                return self.get_person(person)
        return rec

    def create_person(self, person, person_id=None):
        rec = QtSql.QSqlRecord()
        rec.append(QtSql.QSqlField('code', QtCore.QVariant.String))
        rec.setValue('code', QtCore.QVariant(person['TabNumber']))
        rec.append(QtSql.QSqlField('federalCode', QtCore.QVariant.String))
        rec.setValue('federalCode', QtCore.QVariant(person['TabNumber']))
        rec.append(QtSql.QSqlField('regionalCode', QtCore.QVariant.String))
        rec.setValue('regionalCode', QtCore.QVariant(person['TabNumber']))
        rec.append(QtSql.QSqlField('firstName', QtCore.QVariant.String))
        rec.setValue('firstName', QtCore.QVariant(person['Name']))
        rec.append(QtSql.QSqlField('lastName', QtCore.QVariant.String))
        rec.setValue('lastName', QtCore.QVariant(person['Surname']))
        rec.append(QtSql.QSqlField('patrName', QtCore.QVariant.String))
        rec.setValue('patrName', QtCore.QVariant(person['Patroname']))
        rec.append(QtSql.QSqlField('sex', QtCore.QVariant.Int))
        rec.setValue('sex', QtCore.QVariant(person['Sex']))
        rec.append(QtSql.QSqlField('post_id', QtCore.QVariant.Int))
        if person['PostGUID'] in self.posts:
            rec.setValue('post_id', QtCore.QVariant(self.posts[person['PostGUID']]))
        rec.append(QtSql.QSqlField('speciality_id', QtCore.QVariant.Int))
        if person['SpecialityGUID'] in self.specialities:
            rec.setValue('speciality_id', QtCore.QVariant(self.specialities[person['SpecialityGUID']]))
        rec.append(QtSql.QSqlField('orgStructure_id', QtCore.QVariant.Int))
        if person['SubdivisionGUID'] in self.org_structures:
            rec.setValue('orgStructure_id', QtCore.QVariant(self.org_structures[person['SubdivisionGUID']]))
        rec.append(QtSql.QSqlField('SNILS', QtCore.QVariant.String))
        rec.setValue('SNILS', QtCore.QVariant(person['SNILS']))
        rec.append(QtSql.QSqlField('birthDate', QtCore.QVariant.Date))
        rec.setValue('birthDate', QtCore.QVariant(person['DateBirth']))
        rec.append(QtSql.QSqlField('syncGUID', QtCore.QVariant.String))
        rec.setValue('syncGUID', QtCore.QVariant(person['GUID']))
        if person['DateEnd']:
            rec.append(QtSql.QSqlField('retired', QtCore.QVariant.Int))
            rec.append(QtSql.QSqlField('retireDate', QtCore.QVariant.Date))
            rec.setValue('retired', QtCore.QVariant(1))
            rec.setValue('retireDate', QtCore.QVariant(person['DateEnd']))
        if person_id:
            rec.append(QtSql.QSqlField('id', QtCore.QVariant.Int))
            rec.setValue('id', QtCore.QVariant(person_id))
        rec.append(QtSql.QSqlField('org_id', QtCore.QVariant.Int))
        rec.setValue('org_id', QtCore.QVariant(QtGui.qApp.currentOrgId()))
        return rec

    def sync_orders(self, person, person_id):
        if person['SubdivisionGUID'] in self.org_structures:
            os = self.org_structures[person['SubdivisionGUID']]
        else:
            os = 'NULL'

        if person['PostGUID'] in self.posts:
            post = self.posts[person['PostGUID']]
        else:
            post = 'NULL'

        if person['DateBegin'] and not self.db.getCount(self.order_tbl, where=self.db.joinAnd((
                self.order_tbl['master_id'].eq(person_id),
                self.order_tbl['date'].eq(person['DateBegin']),
                self.order_tbl['type'].eq(self.ORDER_BEGIN)
        ))):
            self.db.query(
                self.ORDER_INSERT_QUERY.format(date=person['DateBegin'],
                                               person_id=person_id,
                                               type=self.ORDER_BEGIN,
                                               doc_type=self.begin_docs,
                                               os_id=os,
                                               post_id=post))
        if person['DateEnd'] and not self.db.getCount(self.order_tbl, where=self.db.joinAnd((
                self.order_tbl['master_id'].eq(person_id),
                self.order_tbl['date'].eq(person['DateEnd']),
                self.order_tbl['type'].eq(self.ORDER_RETIRE)
        ))):
            self.db.query(
                self.ORDER_INSERT_QUERY.format(date=person['DateEnd'],
                                               person_id=person_id,
                                               type=self.ORDER_RETIRE,
                                               doc_type=self.retire_docs,
                                               os_id=os,
                                               post_id=post))

    def check_record(self, rec, person):
        diffs = []
        if forceString(rec.value('code')) != person['TabNumber']:
            diffs.append(u'Код')
        if forceString(rec.value('firstName')) != person['Name']:
            diffs.append(u'Имя')
        if forceString(rec.value('lastName')) != person['Surname']:
            diffs.append(u'Фамилия')
        if forceString(rec.value('patrName')) != person['Patroname']:
            diffs.append(u'Отчество')
        if forceString(rec.value('birthDate').toString()) != person['DateBirth']:
            diffs.append(u'Дата рождения')
        if forceInt(rec.value('sex')) != person['Sex']:
            diffs.append(u'Пол')
        if forceString(rec.value('SNILS')) != person['SNILS']:
            diffs.append(u'СНИЛС')
        if person['SubdivisionGUID'] not in (forceString(rec.value('osGUID')) or '') and \
                person['SubdivisionGUID'] in self.org_structures:
            diffs.append(u'Подразделение')
        if person['PostGUID'] not in (forceString(rec.value('postGUID')) or '') and \
                person['PostGUID'] in self.posts:
            diffs.append(u'Должность')
        if person['SpecialityGUID'] not in (forceString(rec.value('specGUID')) or '') and \
                person['SpecialityGUID'] in self.specialities:
            diffs.append(u'Специальность')
        return diffs

    def check_connection(self):
        self.progress.emit(0, 0, u'Проверка соединения с сервисом... ')
        try:
            requests.get(self.url + '?wsdl', timeout=5)
            if self.abort:
                return
            self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/><br/>')
        except requests.ConnectTimeout:
            if self.abort:
                return
            self.progress.emit(0, 0, u'<b><font color=red>Ошибка</font></b><br/>'
                                     u'Не удалось установить соединение с сервисом<br/>'
                                     u'Удостоверьтесь, что в настройках введен адрес, оканчивающийся на ".1cws"<br/>')
            self.abort = True

    def fetch_refbooks(self):
        if self.abort:
            return
        self.progress.emit(0, 0, u'Загрузка справочников... ')
        # OrgStructure
        recs = self.db.getRecordList(
            self.os_tbl,
            (self.os_tbl['id'], self.os_tbl['syncGUID']),
            self.os_tbl['syncGUID'].isNotNull()
        )
        for rec in recs:
            sync_guid = forceString(rec.value('syncGUID'))
            guids = re.findall('([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})', sync_guid, re.IGNORECASE)
            for guid in guids:
                self.org_structures[guid] = forceInt(rec.value('id'))

        # rbPost
        recs = self.db.getRecordList(
            self.post_tbl,
            (self.post_tbl['id'], self.post_tbl['syncGUID']),
            self.post_tbl['syncGUID'].isNotNull()
        )
        for rec in recs:
            sync_guid = forceString(rec.value('syncGUID'))
            guids = re.findall('([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})', sync_guid, re.IGNORECASE)
            for guid in guids:
                self.posts[guid] = forceInt(rec.value('id'))

        # rbSpeciality
        recs = self.db.getRecordList(
            self.spec_tbl,
            (self.spec_tbl['id'], self.spec_tbl['syncGUID']),
            self.spec_tbl['syncGUID'].isNotNull()
        )
        for rec in recs:
            sync_guid = forceString(rec.value('syncGUID'))
            guids = re.findall('([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})', sync_guid, re.IGNORECASE)
            for guid in guids:
                self.specialities[guid] = forceInt(rec.value('id'))

        docs = self.db.getRecordList(self.docs_tbl,
                                     ['id'],
                                     self.docs_tbl['code'].inlist('T-1', 'T-8'),
                                     self.docs_tbl['code'])
        if len(docs) != 2:
            self.progress.emit(0, 0, u'<b><font color=red>Ошибка</font></b><br/>'
                                     u'Не найдены типы документов с кодами T-1 и T-8<br/></br>')
            self.abort = True
            return

        self.begin_docs = forceInt(docs[0].value('id'))
        self.retire_docs = forceInt(docs[1].value('id'))
        self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/><br/>')

    def process_current(self):
        if self.abort:
            return
        self.progress.emit(0, 0, u'Загрузка списка сотрудников... ')
        msg = self.prepare_request('getEmployees', requestDate=self.sync_date)
        headers = {
            'SOAPAction': 'http://www.dkkb.org/1c/Employees#PL_ListEmployees:getEmployees',
        }
        try:
            r = requests.post(self.url, msg, headers=headers, auth=(self.login, self.password))
        except requests.ConnectionError, requests.HTTPError:
            self.progress.emit(0, 0, u'<b><font color=red>Ошибка</font></b><br/>'
                                     u'Не удалось загрузить список сотрудников<br/><br/>')
            self.abort = True
            return
        if self.abort:
            return
        employees = parse_soap_answer(r.content, 'getEmployees')
        self.progress.emit(len(employees), 0, u'<b><font color=green>OK</font></b><br/>'
                                              u'Обработка списка сотрудников... '.format(len(employees)))
        i = 0
        for person in employees:
            if self.abort:
                return
            info_tuple = (person['Subdivision'], person['Post'], person['Speciality'])
            rec = self.get_person(person)
            if not rec:
                if person['SubdivisionGUID'] in self.org_structures:
                    rec = self.create_person(person)
                    self.db.insertRecord(self.person_tbl, rec)
                    rec = self.get_person(person)
                    person_id = forceInt(rec.value('id'))
                    self.stats['created'][person_id] = info_tuple
                    self.sync_orders(person, person_id)
            else:
                person_id = forceInt(rec.value('id'))
                diffs = self.check_record(rec, person)
                if diffs:
                    rec = self.create_person(person, person_id)
                    self.db.updateRecord(self.person_tbl, rec)
                    self.stats['modified'][person_id] = info_tuple + ('/'.join(diffs),)
                self.sync_orders(person, person_id)
            i += 1
            self.progress.emit(len(employees), i, unicode(person_id) + '\n')

        self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/>'
                                 u'Добавлено сотрудников: <b>{}</b><br/>'
                                 u'Установлен код синхронизации: <b>{}</b><br/>'
                                 u'Обновлено сотрудников: <b>{}</b><br/><br/>'.format(
                                                                                         len(self.stats['created']),
                                                                                         len(self.stats['assigned']),
                                                                                         len(self.stats['modified'])
                                                                                     )
                           )

    def process_retired(self):
        if self.abort:
            return
        self.progress.emit(0, 0, u'Загрузка списка уволенных сотрудников... ')
        msg = self.prepare_request('showDismissed', dateStart=self.retire_start, dateEnd=self.retire_end)
        headers = {
            'SOAPAction': 'http://www.dkkb.org/1c/Employees#PL_ListEmployees:showDismissed',
        }
        try:
            r = requests.post(self.url, msg, headers=headers, auth=(self.login, self.password))
        except requests.ConnectionError, requests.HTTPError:
            self.progress.emit(0, 0, u'<b><font color=red>Ошибка</font></b><br/>'
                                     u'Не удалось загрузить список сотрудников<br/>')
            self.abort = True
            return
        if self.abort:
            return
        employees = parse_soap_answer(r.content, 'showDismissed')
        self.progress.emit(len(employees), 0, u'<b><font color=green>OK</font></b><br/>'
                                              u'Обработка списка уволенных сотрудников... '.format(len(employees)))
        i = 0
        for person in employees:
            if self.abort:
                return
            info_tuple = (person['Subdivision'], person['Post'], person['Speciality'])
            rec = self.get_person(person)
            if rec:
                person_id = forceInt(rec.value('id'))
                if person['DateEnd'] and not forceInt(rec.value('retired')):
                    rec = self.db.getRecord(self.person_tbl, ('id', 'retired', 'retireDate'), person_id)
                    rec.setValue('retireDate', person['DateEnd'])
                    rec.setValue('retired', 1)
                    self.db.updateRecord(self.person_tbl, rec)
                    self.stats['retired'][person_id] = info_tuple
                self.sync_orders(person, person_id)
            i += 1
            self.progress.emit(len(employees), i, '')
        self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/>'
                                 u'Уволено сотрудников: <b>{}</b><br/><br/>'.format(len(self.stats['retired'])))

    def check_retired(self):
        if self.abort:
            return
        self.progress.emit(0, 0, u'Установка статусов уволенных сотрудников... ')
        # get last order for each person
        employees = self.db.getRecordList(self.person_tbl, stmt=self.RETIRE_CHECK_QUERY)
        i = 0
        for person in employees:
            if self.abort:
                return
            person_id = forceInt(person.value('id'))
            order_type = forceInt(person.value('type'))
            date = forceString(person.value('date').toDate().toString('yyyy-MM-dd'))
            if order_type == self.ORDER_BEGIN:
                self.db.query(u'UPDATE Person SET retired=\'0\', retireDate=\'\' WHERE id=\'%s\'' % person_id)
            elif order_type == self.ORDER_RETIRE:
                self.db.query(u'UPDATE Person SET retired=\'1\', retireDate=\'%s\' WHERE id=\'%s\'' % (date, person_id))
            i += 1
            self.progress.emit(len(employees), i, '')
        self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/><br/>')

    def run(self):
        self.check_connection()
        self.db.transaction()
        self.fetch_refbooks()
        if self.sync:
            self.process_current()
        if self.retire:
            self.process_retired()
        self.check_retired()
        if not self.abort:
            self.db.query("UPDATE Person SET retireDate=NULL WHERE retireDate='0000-00-00'")
            self.db.commit()
            self.progress.emit(0, 0, u'<br/><font color=green>Синхронизация завершена</font><br/><br/><br/>')
        else:
            self.db.rollback()
            self.progress.emit(0, 0, u'<br/><font color=red>Все изменения отменены</font><br/><br/><br/>')
        self.done.emit(self.stats)
        self.reset()


class ReportWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int, int, unicode)  # total, value, message
    done = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ReportWorker, self).__init__(parent)
        self.db = QtGui.qApp.db
        self.person_tbl = self.db.table('Person')
        self.tbl = self.person_tbl
        self.os_tbl = self.db.table('OrgStructure')
        self.tbl = self.tbl.leftJoin(self.os_tbl, self.person_tbl['orgStructure_id'].eq(self.os_tbl['id']))
        self.post_tbl = self.db.table('rbPost')
        self.tbl = self.tbl.leftJoin(self.post_tbl, self.person_tbl['post_id'].eq(self.post_tbl['id']))
        self.spec_tbl = self.db.table('rbSpeciality')
        self.tbl = self.tbl.leftJoin(self.spec_tbl, self.person_tbl['speciality_id'].eq(self.spec_tbl['id']))

        self.cols = (
            self.person_tbl['id'].alias('id'),
            self.person_tbl['code'].alias('code'),
            self.person_tbl['firstName'].alias('firstName'),
            self.person_tbl['lastName'].alias('lastName'),
            self.person_tbl['patrName'].alias('patrName'),
            self.os_tbl['name'].alias('orgStructure'),
            self.post_tbl['name'].alias('post'),
            self.spec_tbl['name'].alias('speciality'),
        )

        self.stats = {}
        self.file_path = ''

        xlwt.add_palette_colour('missing', 0x21)
        self.missing_style = xlwt.easyxf('pattern: pattern solid, fore_colour missing')

    def set_stats(self, stats, file_path):
        self.stats = stats
        self.file_path = file_path

    @staticmethod
    def create_header(sheet):
        sheet.write(0, 0, u'Код')
        sheet.write(0, 1, u'Фамилия')
        sheet.write(0, 2, u'Имя')
        sheet.write(0, 3, u'Отчество')
        sheet.write(0, 4, u'Подразделение')
        sheet.write(0, 5, u'Должность')
        sheet.write(0, 6, u'Специальность')
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)

    def write_person(self, sheet, person, info_tuple, row):
        code = forceString(person.value('code'))
        last_name = forceString(person.value('lastName'))
        first_name = forceString(person.value('firstName'))
        patr_name = forceString(person.value('patrName'))
        org_structure = forceString(person.value('orgStructure'))
        post = forceString(person.value('post'))
        speciality = forceString(person.value('speciality'))
        sheet.write(row, 0, code)
        sheet.write(row, 1, last_name)
        sheet.write(row, 2, first_name)
        sheet.write(row, 3, patr_name)

        if org_structure:
            sheet.write(row, 4, org_structure)
        elif info_tuple[0]:
            sheet.write(row, 4, info_tuple[0], self.missing_style)

        if post:
            sheet.write(row, 5, post)
        elif info_tuple[1]:
            sheet.write(row, 5, info_tuple[1], self.missing_style)

        if speciality:
            sheet.write(row, 6, speciality)
        elif info_tuple[2]:
            sheet.write(row, 6, info_tuple[2], self.missing_style)

    def run(self):
        try:
            workbook = xlwt.Workbook()
            workbook.set_colour_RGB(0x21, 0xf9, 0x98, 0x75)  # rgb = #f99875

            self.progress.emit(0, 0, u'Запись добавленных сотрудников... ')
            created_sheet = workbook.add_sheet(u'Добавленные (%d)' % len(self.stats['created']))
            self.create_header(created_sheet)
            employees = self.db.getRecordList(self.tbl, self.cols,
                                              self.person_tbl['id'].inlist(self.stats['created'].keys()))
            for row, person in enumerate(employees):
                person_id = forceInt(person.value('id'))
                self.write_person(created_sheet, person, self.stats['created'][person_id], row+1)

            self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/>'
                                     u'Запись измененных сотрудников... ')
            modified_sheet = workbook.add_sheet(u'Измененные (%d)' % len(self.stats['modified']))
            self.create_header(modified_sheet)
            modified_sheet.write(0, 7, u'Изменившиеся поля')
            employees = self.db.getRecordList(self.tbl,
                                              self.cols,
                                              self.person_tbl['id'].inlist(self.stats['modified'].keys()))
            for row, person in enumerate(employees):
                person_id = forceInt(person.value('id'))
                self.write_person(modified_sheet, person, self.stats['modified'][person_id], row+1)
                modified_sheet.write(row+1, 7, self.stats['modified'][forceInt(person.value('id'))][3])

            self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/>'
                                     u'Запись уволенных сотрудников... ')
            retired_sheet = workbook.add_sheet(u'Уволенные (%d)' % len(self.stats['retired']))
            self.create_header(retired_sheet)
            employees = self.db.getRecordList(self.tbl, self.cols,
                                              self.person_tbl['id'].inlist(self.stats['retired'].keys()))
            for row, person in enumerate(employees):
                person_id = forceInt(person.value('id'))
                self.write_person(retired_sheet, person, self.stats['retired'][person_id], row+1)

            self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/>'
                                     u'Запись синхронизированных сотрудников... ')
            assigned_sheet = workbook.add_sheet(u'Синхронизированные (%d)' % len(self.stats['assigned']))
            self.create_header(assigned_sheet)
            employees = self.db.getRecordList(self.tbl, self.cols,
                                              self.person_tbl['id'].inlist(self.stats['assigned'].keys()))
            for row, person in enumerate(employees):
                person_id = forceInt(person.value('id'))
                self.write_person(assigned_sheet, person, self.stats['assigned'][person_id], row+1)
            self.progress.emit(0, 0, u'<b><font color=green>OK</font></b><br/><br/>')

            workbook.save(self.file_path)
        except IOError:
            self.progress.emit(0, 0, u'<b><font color=red>Ошибка при сохранении отчета</font></b><br/><br/>')
        self.done.emit()


class ImportDKKBPersonsDialog(CDialogBase, Ui_ImportDKKBPersonsDialog):
    def __init__(self, login, password, url, parent=None):
        super(ImportDKKBPersonsDialog, self).__init__(parent)
        self.setupUi(self)

        self.worker = Worker(self)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.done.connect(self.on_worker_done)
        self.worker.error.connect(self.on_worker_error)

        self.report_worker = ReportWorker(self)
        self.report_worker.progress.connect(self.on_worker_progress)
        self.report_worker.done.connect(self.on_report_done)

        self.btnStart.clicked.connect(self.start_import)
        self.btnStop.clicked.connect(self.stop_import)
        self.btnReport.clicked.connect(self.save_report)
        self.btnClose.clicked.connect(self.on_close)

        self.login = login
        self.password = password
        self.url = url

        self.stats = dict()

        self.loadDialogPreferences()

    def start_import(self):
        self.btnStart.setEnabled(False)
        self.btnReport.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.btnClose.setEnabled(False)
        self.progressBar.setTextVisible(True)
        self.worker.set_credentials(
            self.url,
            self.login,
            self.password,
            self.chkCurrent.isChecked(),
            forceString(self.edtDateCurrent.date().toString('yyyy-MM-dd')),
            self.chkRetired.isChecked(),
            forceString(self.edtRetiredStart.date().toString('yyyy-MM-dd')),
            forceString(self.edtRetiredEnd.date().toString('yyyy-MM-dd'))
        )
        self.worker.start()

    def stop_import(self):
        self.btnStop.setEnabled(False)
        self.on_worker_progress(0, 0, u'<br/>Остановка синхронизации...')
        self.worker.abort = True

    def save_report(self):
        self.btnStart.setEnabled(False)
        self.btnReport.setEnabled(False)
        self.btnClose.setEnabled(False)
        save_path = QtGui.QFileDialog() \
            .getSaveFileName(self,
                             u'Сохранить отчет',
                             path.join(forceString(
                                 QtGui.QDesktopServices().storageLocation(QtGui.QDesktopServices.DocumentsLocation)
                             ),
                                 'report.xls'),
                             u'XLS файл (*.xls)')
        if save_path:
            self.report_worker.set_stats(self.stats, save_path)
            self.report_worker.start()

    def on_worker_progress(self, total, value, message):
        self.progressBar.setRange(0, total)
        self.progressBar.setValue(value)
        if message:
            self.txtLog.moveCursor(QtGui.QTextCursor.End)
            self.txtLog.insertHtml(message)

    def on_worker_done(self, stats):
        self.stats = stats
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        self.btnReport.setEnabled(True)
        self.btnClose.setEnabled(True)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)

    def on_worker_error(self, message):
        self.txtLog.insertPlainText(message)

    def on_report_done(self):
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.btnStart.setEnabled(True)
        self.btnReport.setEnabled(True)
        self.btnClose.setEnabled(True)

    def on_close(self):
        self.close()

    def closeEvent(self, evt):
        self.saveDialogPreferences()

    def savePreferences(self):
        pref = super(ImportDKKBPersonsDialog, self).savePreferences()
        pref.update({
            'current': self.chkCurrent.isChecked(),
            'retired': self.chkRetired.isChecked(),
            'current_date': self.edtDateCurrent.date(),
            'retire_start': self.edtRetiredStart.date(),
            'retire_end': self.edtRetiredEnd.date()
        })
        return pref

    def loadPreferences(self, preferences):
        super(ImportDKKBPersonsDialog, self).loadPreferences(preferences)
        self.chkCurrent.setChecked(forceBool(getPref(preferences, 'current', True)))
        self.chkRetired.setChecked(forceBool(getPref(preferences, 'retired', True)))
        self.edtDateCurrent.setDate(forceDate(getPref(preferences, 'current_date', QtCore.QDate().currentDate())))
        self.edtRetiredStart.setDate(forceDate(getPref(preferences, 'retire_start', QtCore.QDate().currentDate())))
        self.edtRetiredEnd.setDate(forceDate(getPref(preferences, 'retire_end', QtCore.QDate().currentDate())))
