# -*- coding: utf-8 -*-
STMT_Sections = u'''
    SELECT
        rbEpicrisisSections.id              AS          id
    FROM
        rbEpicrisisTemplates
        LEFT JOIN rbEpicrisisTemplates_rbEpicrisisSections ON rbEpicrisisTemplates_rbEpicrisisSections.id_rbEpicrisisTemplates = rbEpicrisisTemplates.id
        LEFT JOIN rbEpicrisisSections ON rbEpicrisisSections.id = rbEpicrisisTemplates_rbEpicrisisSections.id_rbEpicrisisSections
    WHERE
        rbEpicrisisTemplates.id = %i ORDER BY idx
'''

STMT_Property = u'''
    SELECT
        rbEpicrisisProperty.id              AS          id,
        rbEpicrisisProperty.name            AS          propName,
        rbEpicrisisProperty.type            AS          propType,
        rbEpicrisisProperty.defaultValue    AS          propDef
    FROM
        rbEpicrisisTemplates
        INNER JOIN rbEpicrisisTemplates_rbEpicrisisSections ON rbEpicrisisTemplates_rbEpicrisisSections.id_rbEpicrisisTemplates = rbEpicrisisTemplates.id
        INNER JOIN rbEpicrisisSections ON rbEpicrisisSections.id = rbEpicrisisTemplates_rbEpicrisisSections.id_rbEpicrisisSections
        INNER JOIN rbEpicrisisSections_rbEpicrisisProperty ON rbEpicrisisSections_rbEpicrisisProperty.id_rbEpicrisisSections = rbEpicrisisSections.id
        INNER JOIN rbEpicrisisProperty ON rbEpicrisisProperty.id = rbEpicrisisSections_rbEpicrisisProperty.id_rbEpicrisisProperty
    WHERE
        rbEpicrisisTemplates.id = %i AND rbEpicrisisSections.id = %i
'''