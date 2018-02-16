#!/usr/bin/env python
# -*- coding: utf-8 -*-

CONTENT = u"""

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    
<html>
<head>
<!--Главный скрипт-->
{: clients = dict([])}
{for: event in events}
	{ clients.data.setdefault(event.bedCode, []).append(event)}
{end:}

{: client_num = 0}
{for: bed_name in clients.data}
	{: client_num += len(clients.data[bed_name])}
{end:}
{: rooms = clients.data.keys()}
{: rooms.sort()}
{: NUMSTR = 44}
{: num_pages = (len(events) + len(rooms)-2)/(NUMSTR*2) + 1}
{: finances = [u'Б', u'ОМС', u'ДМС', u'ПМУ', u'ВМП']}
{: space = 0}
{: FirstSpace = ' '}
<!--Конец главного скрипта-->

<!--Проверка необходимости в дополнительной странице-->
{: end_loop = 0}
{for: current_page in xrange(num_pages)}
    {: current_number = 0}
    {for: bed_name in rooms}
        {if: len(bed_name) and not end_loop}
            {if: current_number >=  (NUMSTR*2*current_page - space ) and current_number < (NUMSTR*2*current_page + NUMSTR - space )}     
                {: s = (len(clients.data[bed_name]) + 1) - (NUMSTR*2*current_page + NUMSTR - current_number - space)}
                {if: s > 0}
                    {: space = space + (len(clients.data[bed_name]) + 1) - s}
                    {: current_number = current_number + 100500}
                    {: end_loop = 1}
                    {if: FirstSpace == ' '}
                        {: FirstSpace = 'Left'}
                    {end:}
                {end:}
            {end:}
            {: current_number = current_number + 1}
        {end:}
        
        {:current_number = current_number + len(clients.data[bed_name])}
    {end:}

    {: current_number = 0}
    {for: bed_name in rooms}
        {if: len(bed_name)}
            {if: current_number >= (NUMSTR*2*current_page + NUMSTR - space) and current_number < (NUMSTR*2*current_page + NUMSTR*2 - space)}
                {: s = space + (len(clients.data[bed_name] ) + 1) - (NUMSTR*2*current_page + NUMSTR*2 - current_number)}
                {if: s > 0}
                    {: space = space + s - (len(clients.data[bed_name]) + 1)}
                    {: current_number = current_number + 100500}
                    {if: FirstSpace == ' '}
                        {: FirstSpace = 'Right'}
                    {end:}
                {end:}
            {end:}
            {: current_number = current_number + 1}
        {end:}
        {:current_number = current_number + len(clients.data[bed_name])}
    {end:}
{end:}
<!--Конец проверки-->
{: num_pages = (len(events) + len(rooms) + space - 2)/(NUMSTR*2)  + 1}
{: space = 0}
{: FirstSpace = ' '}

<meta name="qrichtext" content="1" />
</head>
<body style=" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:200; font-style:normal;">
<center>Присутствующие на отделении {orgStructure} (температурный лист) на {currentDate} {client_num} пациентов на отделении.</center>

{for: current_page in xrange(num_pages)}
    {if: current_page > 0}
        <!--НОВАЯ СТРАНИЦА-->
        <p style="page-break-after: always"><font color=#FFFFFF>.</font></p>
    {end:}


    <table cellpadding=0 cellspacing=0 width=100% border="1">
    <tr valign="top"><td width=50%>
    <table width=100% border=1>
    <tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td></tr>
    <tr><td width="8%" height="11pt">И</td><td width="8%" height="11pt">Рег.</td><td width="42%" height="11pt">ФИО</td><td width="12%" height="11pt">утро</td><td width="15%" height="11pt">вечер</td><td width="15%" height="11pt">пит.</td></tr>
    {: current_number = 0}
    {for: bed_name in rooms}
        {if: bed_name!=''}
            {if: current_number >=  (NUMSTR*2*current_page - space ) and current_number < (NUMSTR*2*current_page + NUMSTR - space )}     
                {: s = (len(clients.data[bed_name]) +1) - (NUMSTR*2*current_page + NUMSTR - current_number - space)}
                {if: s > 0}
                    {: space = space + (len(clients.data[bed_name]) + 1) - s}
                    {: current_number = current_number + NUMSTR}
                    {if: FirstSpace == ' '}
                        {: FirstSpace = 'Left'}
                    {end:}
                {end:}
            {end:}
            {if: current_number >=  (NUMSTR*2*current_page - space ) and current_number < (NUMSTR*2*current_page + NUMSTR - space)}
                <tr><td colspan=6 align=center><b>{bed_name}</b></td></tr>
            {end:}
            {: current_number = current_number + 1}
        {end:}
        {for: event in clients.data[bed_name]}
            {if: current_number >=  (NUMSTR*2*current_page - (space-1)) and current_number < (NUMSTR*2*current_page + NUMSTR - (space-1))}
                <tr>
                <!--источник финансирования -->
                {if: event.finance != u'целевой'}
                    <td>{event.finance}</td>
                {else:}
                    <td>{u'ВМП' if event.action[u"Квота"].value.type.class_ == 0 else u'СМП'}</td>
                {end:}
                <!-- местный/неместный -->
                {if: event.client.locAddress.KLADRCode[:2] == '78'}
                    <td></td> 
                {elif: event.client.locAddress.KLADRCode[:2] == '47'}
                    <td>{u'ЛО'}</td> 
                {else:}
                    <td>{' X'}</td>
                {end:}
                <!--ФИО-->
                <td>{event.client.shortName}</td>
                <!--утро и вечер не заполняем -->
                <td></td><td width="15%"></td>
                <!--питание -->
                <td>{event.feed}</td>
                </tr>
            {end:}
            {: current_number = current_number + 1}
        {end:}
    {end:}
    </table></td>

    <td width=50%><table width=100% border=1>
    <tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td></tr>
    <tr><td width="8%" height="11pt">И</td><td width="8%" height="11pt">Рег.</td><td width="42%" height="11pt">ФИО</td><td width="12%" height="11pt">утро</td><td width="15%" height="11pt">вечер</td><td width="15%" height="11pt">пит.</td></tr>
    {: current_number = 0}
    {for: bed_name in rooms}
        {if: bed_name!=''}
            {if: current_number >= (NUMSTR*2*current_page + NUMSTR - space) and current_number < (NUMSTR*2*current_page + NUMSTR*2 - space)}
                {: s = space + (len(clients.data[bed_name]) + 1) - (NUMSTR*2*current_page + NUMSTR*2 - current_number)}
                {if: s > 0}
                    {: space = space + (len(clients.data[bed_name]) + 1) - s}
                    {: current_number = current_number + NUMSTR}
                    {if: FirstSpace == ' '}
                        {: FirstSpace = 'Right'}
                    {end:}
                {end:}
            {end:}
            {if: current_number >= (NUMSTR*2*current_page + NUMSTR - space) and current_number < (NUMSTR*2*current_page + NUMSTR*2 - space)}
                <tr><td colspan=6 align=center><b>{bed_name}</b></td></tr>
            {end:}
            {: current_number = current_number + 1}
        {end:}
        {for: event in clients.data[bed_name]}
            {if: current_number >=  (NUMSTR*2*current_page + NUMSTR - (space-1)) and current_number < (NUMSTR*2*current_page + NUMSTR*2 - (space-1))}
                <tr>
                <!--источник финансирования -->
                {if: event.finance != u'целевой'}
                    <td>{event.finance}</td>
                {else:}
                    <td>{u'ВМП' if event.action[u"Квота"].value.type.class_ == 0 else u'СМП'}</td>
                {end:}
                <!-- местный/неместный -->
                {if: event.client.locAddress.KLADRCode[:2] == '78'}
                    <td></td> 
                {elif: event.client.locAddress.KLADRCode[:2] == '47'}
                    <td>{u'ЛО'}</td> 
                {else:}
                    <td>{' X'}<!--{event.client.locAddress.city[:24]} --></td>
                {end:}
                <!--ФИО-->
                <td>{event.client.shortName}</td>
                <!--утро и вечер не заполняем -->
                <td></td><td></td>
                <!--питание -->
                <td>{event.feed}</td>
                </tr>
            {end:}
            {: current_number = current_number + 1}
        {end:}
    {end:}
    </table></td>
    </tr></table>
{end:}
</body>
</html>"""
