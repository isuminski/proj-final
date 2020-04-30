### IMPORTS ###
from bs4 import BeautifulSoup
import requests
import json

### GLOBAL VARIABLES ###
CACHE_FILENAME = 'practice-cache-file.json'
CACHE_DICT = {}

BASE_URL = 'https://webbook.nist.gov/cgi/fluid.cgi'
PARAMS = {'Action' : 'Load',
          'ID' : 'C7732185',
          'Type' : 'IsoBar',
          'Digits' : '5',
          'P' : None,
          'TLow' : None,
          'THigh' : None,
          'TInc' : 1,
          'RefState' : 'DEF',
          'TUnit' : 'K',
          'PUnit' : 'bar',
          'DUnit' : 'kg%2Fm3',
          'HUnit' : 'kJ%2Fkg',
          'WUnit' : 'm%2Fs',
          'VisUnit' : 'uPa*s',
          'STUnit' : 'N%2Fm'}

### FUNCTIONS ###
def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def add_to_parameters(Temp, Press):
    global PARAMS
    PARAMS['P'] = Press
    PARAMS['TLow'] = Temp
    PARAMS['THigh'] = Temp
    pass

def make_request_with_cache(base_url, params):
    global CACHE_DICT
    unique_name = json.dumps(params)
    if unique_name in CACHE_DICT:
        print('Using cache...')
        response = CACHE_DICT[unique_name]
    else:
        print('Making request...')
        full_url = BASE_URL + '?'
        for key in params:
            full_url += key + '=' + str(params[key]) + '&'
        full_url = full_url[:-1]
        response = requests.get(full_url).text
        CACHE_DICT[unique_name] = response
        save_cache(CACHE_DICT)
    return response
    
def scrape_info(html):
    Soup = BeautifulSoup(html, 'html.parser')
    row = Soup.find('table', class_='small').find_all('tr')[1]
    columns = row.find_all('td')
    h = columns[5].get_text()
    phase = columns[-1].get_text()
    info_str = 'Enthalpy : ' + h + ' (' + phase + ')'
    print(info_str)
    pass

if __name__ == '__main__':
    
    CACHE_DICT = open_cache()
    
    while True:
        TempPress = input('Input Temp (K) and Pressure (P) separated by a space: ')
        if TempPress == 'exit':
            break
        elif (len(TempPress.split(' ')) == 2
              and TempPress.split(' ')[0].isnumeric()
              and TempPress.split(' ')[1].isnumeric()
              and eval(TempPress.split(' ')[0]) < 1200
              and eval(TempPress.split(' ')[1]) < 800):
            T = TempPress.split(' ')[0]
            P = TempPress.split(' ')[1]
            add_to_parameters(T, P)
            html = make_request_with_cache(BASE_URL, PARAMS)
            scrape_info(html)
        else:
            print("BAD INPUT! ('exit' to exit program)")
        continue
    
    
    