### DATA ACCESS PRACTICE ###

### IMPORTS ###
from bs4 import BeautifulSoup
import requests
import json

### NOTES ###
# Isobaric example URL
'https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=IsoBar&Digits=5&P=150&THigh=950&TLow=300&TInc=10&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'
# Isothermal example URL
'https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=IsoTherm&Digits=5&PLow=1&PHigh=300&PInc=0.5&T=950&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'

'''
Isobaric ULR parameters:
    Action=Load
    ID=C7732185
    Type=IsoBar
    Digits=5
    P=150
    THigh=950
    TLow=300
    TInc=10
    RefState=DEF
    TUnit=K
    PUnit=bar
    DUnit=kg%2Fm3
    HUnit=kJ%2Fkg
    WUnit=m%2Fs
    VisUnit=uPa*s
    STUnit=N%2Fm
'''

'''
Isothermal URL parameters:
    Action=Load
    ID=C7732185
    Type=IsoTherm
    Digits=5
    PLow=1
    PHigh=300
    PInc=0.5
    T=950
    RefState=DEF
    TUnit=K
    PUnit=bar
    DUnit=kg%2Fm3
    HUnit=kJ%2Fkg
    WUnit=m%2Fs
    VisUnit=uPa*s
    STUnit=N%2Fm
'''

'''
Things to note:
    Isothermal vs. Isobaric needs to be determined by program
    Probably best if High/Low and Increments are automated also.
    
'''
# Fluid type and units (same for all states)
ID = 'C7732185'
TUnit = 'K'
PUnit = 'bar'
DUnit = 'kg%2Fm3'
HUnit = 'kJ%2Fkg'
WUnit = 'm%2Fs'

# Variable Parameters (will change from state to state)
# Isobaric
P = 150
TLow = 300
THigh = 950
TInc = 10
# Isothermal
PLow = 0.5
PHigh = 200
PInc = 0.5
T = 950



BASE_URL = 'https://webbook.nist.gov/cgi/fluid.cgi'

PPARAM = {'Action' : 'Load',
          'ID' : ID,
          'Type' : 'IsoBar',
          'Digits' : '5',
          'P' : P,
          'TLow' : TLow,
          'THigh' : THigh,
          'TInc' : TInc,
          'RefState' : 'DEF',
          'TUnit' : TUnit,
          'PUnit' : PUnit,
          'DUnit' : DUnit,
          'HUnit' : HUnit,
          'WUnit' : WUnit,
          'VisUnit' : 'uPa*s',
          'STUnit' : 'N%2Fm'}

TPARAM = {'Action' : 'Load',
          'ID' : ID,
          'Type' : 'IsoTherm',
          'Digits' : '5',
          'PLow' : PLow,
          'PHigh' : PHigh,
          'PInc' : PInc,
          'T' : T,
          'RefState' : 'DEF',
          'TUnit' : TUnit,
          'PUnit' : PUnit,
          'DUnit' : DUnit,
          'HUnit' : HUnit,
          'WUnit' : WUnit,
          'VisUnit' : 'uPa*s',
          'STUnit' : 'N%2Fm'}

SatPARAM = {'Action' : 'Load',
          'ID' : 'C7732185',
          'Type' : 'SatP',
          'Digits' : '5',
          'THigh' : 300,
          'TLow' : 300,
          'TInc' : 0,
          'RefState' : 'DEF',
          'TUnit' : 'K',
          'PUnit' : 'bar',
          'DUnit' : 'kg%2Fm3',
          'HUnit' : 'kJ%2Fkg',
          'WUnit' : 'm%2Fs',
          'VisUnit' : 'Pa*s',
          'STUnit' : 'N%2Fm'}

'''Action=Load
ID=C7732185
Type=SatP
Digits=5
THigh=300
TLow=300
TInc=0
RefState=DEF
TUnit=K
PUnit=bar
DUnit=kg%2Fm3
HUnit=kJ%2Fkg
WUnit=m%2Fs
VisUnit=Pa*s
STUnit=N%2Fm'''

Presponse = requests.get(BASE_URL, PPARAM)
# Tresponse = requests.get(BASE_URL, TPARAM)

# SatResponse = requests.get(BASE_URL, SatPARAM)
full_url = BASE_URL + '?'
for key in SatPARAM:
    full_url += key + '=' + str(SatPARAM[key]) + '&'
full_url = full_url[:-1]
print(full_url)

SatResponse = requests.get(full_url)

# print(Presponse.text)
# print(Tresponse.text)
# print('IsoBaric Response Code:', Presponse.status_code)
# print('IsoThermal Response Code:', Tresponse.status_code)

Psoup = BeautifulSoup(Presponse.text, 'html.parser')
# Get Table Rows
# All output tables have the same format/column order
# making retreiving specific information easier.
Prows = Psoup.find('table', class_='small').find_all('tr')[1:]
print(Prows)

SatSoup = BeautifulSoup(SatResponse.text, 'html.parser')
row_t = SatSoup.find_all('table', class_='small')[0].find_all('tr')[0]
row_f = SatSoup.find_all('table', class_='small')[0].find_all('tr')[1].find_all('td')
row_v = SatSoup.find_all('table', class_='small')[1].find_all('tr')[1].find_all('td')
print()
print(row_t)
print()
print(row_f)
print(row_v)
print('enthalpy, x=0.88')
hf = eval(row_f[5].get_text())
hv = eval(row_v[5].get_text())
print(hf, hv)
h = hf + 0.88 * (hv-hf)
print(h)

# Getting a unique key for cache!
# unique_key = json.dumps(TPARAM)
# print(unique_key)

