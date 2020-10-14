# INA226 Config register calculator

# Lists of possible register settings
liste_AVG = [['1', '0x0000'],['4', '0x0200'],['16', '0x0400'],['64', '0x0600'],['128', '0x0800'],['256', '0x0A00'],['512', '0x0C00'],['1024', '0x0E00'] ]

liste_VBUSCT = [['140','0x0000'],['204','0x0040'],['332','0x0080'],['588','0x00C0'],['1100','0x0100'],['2116','0x0140'],['4156','0x0180'],['8244','0x01C0']]

liste_VSHCT = [['140','0x0000'],['204','0x0008'],['332','0x0010'],['588','0x0018'],['1100','0x0020'],['2116','0x0028'],['4156','0x0030'],['8244','0x0038']]

liste_MODE = [['OFF1','0x0000'],['SHV_TRIG','0x0001'],['BUSV_TRIG','0x0002'],['SHBUSV_TRIG','0x0003'],['OFF2','0x0004'],['SHV_CONT','0x0005'],['BUSV_CONT','0x0006'],['SHBUS_CONT','0x0007']]

constant_bits = 0x4000

# Structure of the config register
# constant_bits + AVG + VBUSCT + VSHCT + MODE

def sucher(wert, liste):
    for element in liste:
        if element[0] == wert:
            # print(element)
            return element[1]

def listeguck(liste):
    for element in liste:
        print('{}: {}'.format(element[0], element[1]))

def registern():
    listeguck(liste_AVG)
    auswahl_avg_input = input('Please input sample number: ')
    auswahl_avg = int(sucher(auswahl_avg_input, liste_AVG), 16)

    listeguck(liste_VBUSCT)
    auswahl_VBUSCT_input = input('Please input VBUS conversion time: ')
    auswahl_VBUSCT = int(sucher(auswahl_VBUSCT_input, liste_VBUSCT), 16)

    listeguck(liste_VSHCT)
    auswahl_VSHCT_input = input('Please input VSHUNT conversion time: ')
    auswahl_VSHCT = int(sucher(auswahl_VSHCT_input, liste_VSHCT), 16)

    listeguck(liste_MODE)
    auswahl_MODE_input = input('Please input operating mode: ')
    auswahl_MODE = int(sucher(auswahl_MODE_input, liste_MODE), 16)

    print('{} {} {} {} {}'.format(constant_bits, auswahl_avg, auswahl_VBUSCT, auswahl_VSHCT, auswahl_MODE))
    register = hex(constant_bits + auswahl_avg + auswahl_VBUSCT + auswahl_VSHCT + auswahl_MODE)
    print('Value for the configuration register: ')
    print(register)
    return register

# print(type(sucher(input('wert: '), liste_MODE)))

status = True

while status:
    try:
        registern()
        weiter = input('Nochmal? (j/n): ')
        if weiter == 'n':
            status = False
    except:
        status = False
        print('uh-oh!')
