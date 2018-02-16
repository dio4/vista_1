# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtSvg
from DentalFormula import TOOTH_SIZE, ToothSchemaDelegate


def gen_tooth_svg(tooth, size=TOOTH_SIZE):
    r = QtCore.QRect(0, 0, size, size)
    out = QtCore.QByteArray()
    buf = QtCore.QBuffer(out)

    gen = QtSvg.QSvgGenerator()
    gen.setSize(QtCore.QSize(size, size))
    gen.setViewBox(QtCore.QRect(-1, -1, size + 2, size + 2))
    gen.setOutputDevice(buf)
    painter = QtGui.QPainter()
    painter.begin(gen)
    painter.setBrush(QtGui.QBrush(QtCore.Qt.white))

    sections = tooth.sections
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setPen(QtGui.QPen(QtCore.Qt.black))
    painter.setFont(ToothSchemaDelegate.get_font(float(size) / TOOTH_SIZE))

    x, y, w, h = r.x(), r.y(), r.width(), r.height()

    if sections.FULL:
        painter.setFont(ToothSchemaDelegate.get_large_font(float(size) / TOOTH_SIZE))
        painter.drawEllipse(r)
        painter.drawText(r, QtCore.Qt.AlignCenter, '\n'.join((state.code for state in sections.FULL)))
        painter.end()
        return unicode(out)

    painter.drawPie(r, 45 * 16, 90 * 16)  # U
    painter.drawPie(r, 135 * 16, 90 * 16)  # L
    painter.drawPie(r, 225 * 16, 90 * 16)  # D
    painter.drawPie(r, 315 * 16, 90 * 16)  # R

    if not tooth.is_simplified():
        r = QtCore.QRect(x + w / 4, y + h / 4, w / 2, h / 2)
        painter.drawPie(r, 90 * 16, 180 * 16)  # CL
        painter.drawPie(r, 270 * 16, 180 * 16)  # CR

        painter.drawText(
            QtCore.QRect(x, y, w / 4, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.L))
        )
        painter.drawText(
            QtCore.QRect(x, y, w, h / 4),
            QtCore.Qt.AlignCenter,
            ' '.join((state.code for state in sections.U))
        )
        painter.drawText(
            QtCore.QRect(x + w * 3 / 4, y, w / 4, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.R))
        )
        painter.drawText(
            QtCore.QRect(x, y + h * 3 / 4, w, h / 4),
            QtCore.Qt.AlignCenter,
            ' '.join((state.code for state in sections.D))
        )
        painter.drawText(
            QtCore.QRect(x + w / 4, y, w / 4, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.CL))
        )
        painter.drawText(
            QtCore.QRect(x + w * 2 / 4, y, w / 4, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.CR))
        )
    else:
        painter.drawText(
            QtCore.QRect(x, y, w / 2, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.L))
        )
        painter.drawText(
            QtCore.QRect(x, y, w, h / 2),
            QtCore.Qt.AlignCenter,
            ' '.join((state.code for state in sections.U))
        )
        painter.drawText(
            QtCore.QRect(x + w / 2, y, w / 2, h),
            QtCore.Qt.AlignCenter,
            '\n'.join((state.code for state in sections.R))
        )
        painter.drawText(
            QtCore.QRect(x, y + h / 2, w, h / 2),
            QtCore.Qt.AlignCenter,
            ' '.join((state.code for state in sections.D))
        )
    painter.end()
    return unicode(out)


def gen_tooth_col(tooth, model, size=TOOTH_SIZE):
    svg = gen_tooth_svg(tooth, size)
    status_obj = model.statuses[tooth.status] if tooth.status else None

    return [
        u'''<td style="background-color: %s">%s</td>''' % (status_obj.color if status_obj else '#fff',
                                                           status_obj.name if status_obj else '---'),
        u'''<td>%s</td>''' % tooth.mobility or u'---',
        u'''<td><img src='data:image/svg+xml;utf8,%s' /></td>''' % svg,
        u'''<td align=center>%s</td>''' % tooth.get_number()
    ]


def formula_printer(model):
    def print_formula(size):
        """ :type model: DentalFormulaModel """
        tbl = [
            [u'<td width=100>Статус</td>'],
            [u'<td>Подвижность</td>'],
            [u'<td>Состояние</td>'],
            [u'<td>Номер</td>'],
            [u'<td>Номер</td>'],
            [u'<td>Состояние</td>'],
            [u'<td>Подвижность</td>'],
            [u'<td>Статус</td>']
        ]
        max_number = 5 if model.is_deciduous else 8
        for number in xrange(10+max_number, 10, -1):
            tooth = model.items[number]
            tooth_col = gen_tooth_col(tooth, model, size)
            tbl[0] += [tooth_col[0]]
            tbl[1] += [tooth_col[1]]
            tbl[2] += [tooth_col[2]]
            tbl[3] += [tooth_col[3]]
        for number in xrange(21, 21+max_number):
            tooth = model.items[number]
            tooth_col = gen_tooth_col(tooth, model, size)
            tbl[0] += [tooth_col[0]]
            tbl[1] += [tooth_col[1]]
            tbl[2] += [tooth_col[2]]
            tbl[3] += [tooth_col[3]]
        for number in xrange(30+max_number, 30, -1):
            tooth = model.items[number]
            tooth_col = gen_tooth_col(tooth, model, size)
            tbl[4] += [tooth_col[3]]
            tbl[5] += [tooth_col[2]]
            tbl[6] += [tooth_col[1]]
            tbl[7] += [tooth_col[0]]
        for number in xrange(41, 41+max_number):
            tooth = model.items[number]
            tooth_col = gen_tooth_col(tooth, model, size)
            tbl[4] += [tooth_col[3]]
            tbl[5] += [tooth_col[2]]
            tbl[6] += [tooth_col[1]]
            tbl[7] += [tooth_col[0]]
        return (u'<table style="color: black; background: white;">%s</table>' %
                u'\n'.join([u'<tr>%s</tr>' % u'\n'.join(row) for row in tbl]))
    return print_formula
