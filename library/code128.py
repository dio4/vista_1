# -*- coding: utf-8 -*-
# "адаптировано" с http://grandzebu.net/index.php?page=/informatique/codbar-en/code128.htm
# кое-что полезное можно подсмотреть на http://barcode128.blogspot.com/

def code128(chaine):

    def alldigits(chaine, start, length):
        return chaine[start:start+length].isdigit() and len(chaine)>=start+length

    result = ''
    if chaine:
        tableB = True
        i = 0 # 'i% devient l'index sur la chaine / i% become the string index
        while i<len(chaine):
            if tableB:
                # Voir si intéressant de passer en table C / See if interesting to switch to table C
                # Oui pour 4 chiffres au début ou à la fin, sinon pour 6 chiffres / yes for 4 digits at start or end, else if 6 digits
                if alldigits(chaine, i, 4 if (i==0 or i+3 == len(chaine)) else 6): # Choix table C / Choice of table C
                    if i == 0: # Débuter sur table C / Starting with table C
                        result = chr(210)
                    else: # Commuter sur table C / Switch to table C
                        result += chr(204)
                    tableB = False
            else:
                if i == 0:
                    result = chr(209) # Débuter sur table B / Starting with table B
            if not tableB:
                # On est sur la table C, essayer de traiter 2 chiffres / We are on table C, try to process 2 digits
                if alldigits(chaine, i, 2): # OK pour 2 chiffres, les traiter / OK for 2 digits, process it
                    dummy = int(chaine[i:i+2])
                    dummy += 32 if dummy < 95 else 105
                    result += chr(dummy)
                    i += 2
                else: # On n'a pas 2 chiffres, repasser en table B / We haven't 2 digits, switch to table B
                    result += chr(205)
                    tableB = True
            if tableB:
                # Traiter 1 caractère en table B / Process 1 digit with table B
                if not( 32<=ord(chaine[i])<=126 ):
                    raise ValueError('character for code128 out of range')
                result += chaine[i]
                i += 1
    if not result:
        result = chr(210) # Débuter sur table C / Starting with table C
    # Calcul de la clé de contrôle / Calculation of the checksum
    for i, c in enumerate(result):
        dummy = ord(c)
        dummy -= 32 if dummy < 127 else 105
        if i == 0:
            checksum = dummy
        else:
            checksum +=  i * dummy
    checksum = checksum % 103
    #'Calcul du code ASCII de la clé / Calculation of the checksum ASCII code
    #
    checksum += 32 if checksum<95 else 105
    # 'Ajout de la clé et du STOP / Add the checksum and the STOP
    result += chr(checksum) + chr(211)
#    return result
    return result.decode('latin1')
