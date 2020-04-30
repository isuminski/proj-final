###############################
##### Name: Ivan Suminski #####
##### uniqname: suminski  #####
###############################

### IMPORTS ###
from math import log10, floor
import requests
import json
import webbrowser
from flask import Flask, render_template, redirect, url_for, request
from bs4 import BeautifulSoup
import sqlite3

### GLOBAL VARIABLES ###
CACHE_DICT = {}
CACHE_FILENAME = 'NIST-cache.json'
DB_NAME = "NIST-database.sqlite"

BASE_URL = BASE_URL = 'https://webbook.nist.gov/cgi/fluid.cgi'

ISIMPERIAL = False
STATE = None


### CLASS DEFINITION ###
class State:
    '''
    States are documented as members of the class State where:
        self.T = temperature
        self.P = pressure
        self.h = specific enthalpy
        self.s = specific entropy
        self.u = specific internal energy
        self.v = specific volume
        
        self.phase = liquid, vapor, or mix
        self.x = quality (None unless state is under the curve)
        self.units = 'metric' OR 'imperial'
        
        self.error = error message(s) associated with request (multi-line string)
'''
    global ISIMPERIAL
    
    def __init__(self, T=None, P=None, h=None, s=None, x=None, ALL=None):
        self.units = ['metric', 'imperial'][ISIMPERIAL]
        if ALL is not None:
            self.T = ALL[0]
            self.P = ALL[1]
            self.h = ALL[2]
            self.s = ALL[3]
            self.x = ALL[4]
            self.v = ALL[5]
            self.u = ALL[6]
            self.phase = ALL[7]
            self.uses = ALL[8] + 1
            self.error = 'Errors:'
            return
        self.error = 'Errors:'
        self.uses = 0
        self.T = T
        self.P = P
        self.h = h
        self.s = s
        self.x = x
        count = 0
        for argument in [T, P, h, s, x]:
            if argument != None:
                count += 1
            continue
        if count > 2:
            self.error += '\n - State is over-constrained! (2 arguments needed to be fully defined.)'
            self.invalid_state()
        elif count < 2:
            self.error += '\n - State is under-constrained! (2 arguments needed to be fully defined.)'
            self.invalid_state()
        else:
            if self.x != None:
                if 0 <= x and x<= 1:
                    if (T == None) ^ (P == None):
                        self.populate_saturation()
                    else:
                        self.error += '\n - Must use Temperature or Pressure for saturation properties!'
                        self.invalid_state()
                        pass
                else:
                    self.error += '\n - Quality must range from 0 to 1!'
                    self.invalid_state()
                    pass
            elif self.T != None:
                if self.T < [274, 32.2][ISIMPERIAL]:
                    self.error += '\n - Temperature is below minimum value!'
                    self.invalid_state()
                elif self.T > [1275, 1835][ISIMPERIAL]:
                    self.error += '\n - Temperature exceeds maximum!'
                    self.invalid_state()
                else:
                    self.populate_isothermal()
            elif self.P != None:
                if self.P > [10000, 145035][ISIMPERIAL]:
                    self.error += '\n - Pressure exceeds maximum!'
                else:
                    self.populate_isobaric()
            else:
                self.populate_hs() 
        pass
    
    
    def populate_saturation(self):
        ''' A function to complete the class initialization in the case
        that the fluid state is one of saturation.
        '''
        global ISIMPERIAL
        if (self.T != None
            and self.T > [273.2, 32.1][ISIMPERIAL]
            and self.T < [647, 705][ISIMPERIAL]):
            parameters = construct_parameters('SatP', {'TLow' : self.T,
                                                       'THigh' : self.T,
                                                       'TInc' : 0})
        elif (self.P != None
              and self.P > [.007, .09][ISIMPERIAL]
              and self.P < [220, 3200][ISIMPERIAL]):
            parameters = construct_parameters('SatT', {'PLow' : self.P,
                                                       'PHigh' : self.P,
                                                       'PInc' : 0})
        else:
            self.error += '\n - Input is not within saturation curve!'
            self.invalid_state()
        response = make_request_with_cache(parameters)
        soup = BeautifulSoup(response, 'html.parser')
        row_f = soup.find_all('table', class_='small')[0].find_all('tr')[1].find_all('td')
        row_v = soup.find_all('table', class_='small')[1].find_all('tr')[1].find_all('td')
        
        if self.T == None:
            self.T = eval(row_f[0].get_text())
        else:
            self.P = eval(row_f[1].get_text())
        v_fv = [eval(row_f[3].get_text()), eval(row_v[3].get_text())]
        u_fv = [eval(row_f[4].get_text()), eval(row_v[4].get_text())]
        h_fv = [eval(row_f[5].get_text()), eval(row_v[5].get_text())]
        s_fv = [eval(row_f[6].get_text()), eval(row_v[6].get_text())]
        self.v = interp_calculation(v_fv, self.x)
        self.u = interp_calculation(u_fv, self.x)
        self.h = interp_calculation(h_fv, self.x)
        self.s = interp_calculation(s_fv, self.x)
        if self.x == 1:
            self.phase = 'vapor-sat.'
        elif self.x == 0:
            self.phase = 'liquid-sat.'
        else:
            self.phase = 'mixture'
        pass
    
    def populate_isothermal(self):
        ''' A function to complete the class initialization in the case
        that an isothermal search is needed.
        '''
        if self.P != None:
            parameters = construct_parameters('IsoTherm', {'PLow' : self.P,
                                                           'PHigh' : self.P,
                                                           'PInc' : 0,
                                                           'T' : self.T})
            response = make_request_with_cache(parameters)
            soup = BeautifulSoup(response, 'html.parser')
            rows = soup.find('table', class_='small').find_all('tr')[1].find_all('td')
            self.v = eval(rows[3].get_text())
            self.u = eval(rows[4].get_text())
            self.h = eval(rows[5].get_text())
            self.s = eval(rows[6].get_text())
            self.phase = rows[-1].get_text()
        elif self.T < [647, 705][ISIMPERIAL] and self.T > [274, 32.1][ISIMPERIAL]:
            parameters = construct_parameters('SatP', {'TLow' : self.T,
                                                       'THigh' : self.T,
                                                       'TInc' : 0})
            response = make_request_with_cache(parameters)
            soup = BeautifulSoup(response, 'html.parser')
            row_f = soup.find_all('table', class_='small')[0].find_all('tr')[1].find_all('td')
            row_v = soup.find_all('table', class_='small')[1].find_all('tr')[1].find_all('td')
            if ((self.h != None
                and eval(row_f[5].get_text()) < self.h
                and eval(row_v[5].get_text()) > self.h) or
                (self.s != None
                 and eval(row_f[6].get_text()) < self.s
                 and eval(row_v[6].get_text()) > self.s)):
                self.find_under_curve(row_f, row_v)
            elif self.h != None:
                self.iterative_search('IsoTherm', self.h)
            else:
                self.iterative_search('IsoTherm', self.s)
        pass
    
    
    def populate_isobaric(self):
        ''' A function to complete the class initialization in the case
        that an isobaric search is needed.
        '''
        if self.P < [220, 3200][ISIMPERIAL] and self.P > [.01, .09][ISIMPERIAL]:
            parameters = construct_parameters('SatT', {'PLow' : self.P,
                                                       'PHigh' : self.P,
                                                       'PInc' : 0})
            response = make_request_with_cache(parameters)
            soup = BeautifulSoup(response, 'html.parser')
            row_f = soup.find_all('table', class_='small')[0].find_all('tr')[1].find_all('td')
            row_v = soup.find_all('table', class_='small')[1].find_all('tr')[1].find_all('td')
            if ((self.h != None
                and eval(row_f[5].get_text()) < self.h
                and eval(row_v[5].get_text()) > self.h) or
                (self.s != None
                 and eval(row_f[6].get_text()) < self.s
                 and eval(row_v[6].get_text()) > self.s)):
                self.find_under_curve(row_f, row_v)
            elif self.h != None:
                self.iterative_search('IsoBar', self.h)
            else:
                self.iterative_search('IsoBar', self.s)
        pass
    
    def populate_hs(self):
        '''A double-interpolation function to complete the class initialization
        in the event that neither temperature nor pressure was provided.  This
        function has not been implemented for this project.
        '''
        self.error += '\n - Interpolation functionality for h-s searches not implemented yet!'
        self.invalid_state()
        pass
    
    def invalid_state(self):
        ''' "Completes" class initialization in the event that an error has occured
        and the dummy-state (all attributes = None) is needed to prevent crashing!
        '''
        self.T = None
        self.P = None
        self.h = None
        self.s = None
        self.x = None
        
        self.u = None
        self.v = None
        self.phase = None
        pass
    
    def iterative_search(self, Type, goal):
        ''' A function designed to complete class initialization in the event
        that EITHER temperature or pressure has been provided, and either
        enthalpy or entropy.
        '''
        global ISIMPERIAL
        LO = {'IsoTherm' : [0.1, 0.1],
              'IsoBar' : [275, 33]}[Type][ISIMPERIAL]
        HI = {'IsoTherm' : [10000.1, 145035.1],
              'IsoBar' : [1275, 1833]}[Type][ISIMPERIAL]
        IN = {'IsoTherm' : [100, 495],
              'IsoBar' : [5, 10]}[Type][ISIMPERIAL]
        compact = [LO, HI, IN]
        formats = {'IsoTherm' : ['PLow', 'PHigh', 'PInc'],
                   'IsoBar' : ['TLow', 'THigh', 'TInc']}
        col = [5, 6][(self.h == None)]
        times = 0
        while self.h == None or self.s == None:
            dictionary = {}
            for i in range(3):
                dictionary[formats[Type][i]] = compact[i]
            if Type == 'IsoTherm':
                dictionary['T'] = self.T
            else:
                dictionary['P'] = self.P
            times += 1
            parameters = construct_parameters(Type, dictionary)
            response = make_request_with_cache(parameters)
            soup = BeautifulSoup(response, 'html.parser')
            rows = soup.find('table', class_='small').find_all('tr')[1:]
            for i in range(len(rows)):
                columns = rows[i].find_all('td')
                if eval(columns[col].get_text()) == goal:
                    if Type == 'IsoTherm':
                        self.P = eval(columns[1].get_text())
                    else:
                        self.T = eval(columns[0].get_text())
                    self.v = eval(columns[3].get_text())
                    self.u = eval(columns[4].get_text())
                    self.h = eval(columns[5].get_text())
                    self.s = eval(columns[6].get_text())
                    self.phase = columns[-1].get_text()
                    return
                elif ((eval(columns[col].get_text()) > goal and Type == 'IsoBar')
                      or eval(columns[col].get_text()) < goal and Type == 'IsoTherm'):
                    compact[1] = eval(columns[Type == 'IsoTherm'].get_text())
                    compact[0] = eval(rows[i-1].find_all('td')[Type == 'IsoTherm'].get_text())
                    if i == 0:
                        self.error += '\n - State may not exist!'
                        self.invalid_state()
                        return
                    elif times == 1:
                        compact[2] = 1
                    else:
                        compact[2] = compact[2]/10
                    break
                elif i == len(rows) - 1:
                    self.error += '\n - State may not exist!'
                    self.invalid_state()
                    return
                else:
                    continue
    pass 
                    
    def find_under_curve(self, row_f, row_v):
        ''' A function for when a state is found to be "under" the saturation
        curve, and interoplation must be done.
        '''
        self.phase = 'mixture'
        col = [5, 6][(self.h == None)]
        if self.h == None:
            y = self.s
        else:
            y = self.h
        
        x = (y-eval(row_f[col].get_text()))/(eval(row_v[col].get_text())-eval(row_f[col].get_text()))
        self.x = x
        if self.P == None:
            self.P = eval(row_f[1].get_text())
        else:
            self.T = eval(row_f[0].get_text())
        for i in range(3,7):
            if i == col:
                continue
            else:
                f = eval(row_f[i].get_text())
                v = eval(row_v[i].get_text())
                val = f + x * (v - f)
                if i == 3:
                    self.v = val
                if i == 4:
                    self.u = val
                if i == 5:
                    self.h = val
                if i == 6:
                    self.s = val
        pass              
            

### FUNCTIONS ###
def open_cache():
    ''' A function to open the cache file and load it into the program
    as a dictionary.

    Returns
    -------
    cache_dict : dict
        large dictionary in which keys are json strings of search parameters
        and contents are large html strings of the returns.

    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' A function to save the cache file
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()
    pass

def make_request_with_cache(params):
    ''' A function to query the NIST online webbooks, using the cache file
    to prevent over-use.
    '''
    global CACHE_DICT
    global BASE_URL
    unique_name = json.dumps(params)
    if unique_name in CACHE_DICT:
        response = CACHE_DICT[unique_name]
    else:
        full_url = BASE_URL + '?'
        for key in params:
            full_url += key + '=' + str(params[key]) + '&'
        full_url = full_url[:-1]
        response = requests.get(full_url).text
        CACHE_DICT[unique_name] = response
        save_cache(CACHE_DICT)
    return response

def construct_parameters(search_type, dictionary):
    ''' Helper function to complete search parameters depending on the 
    specifics of the search needed
    '''
    global ISIMPERIAL
    base_params = {'Action' : 'Load',
                   'ID' : 'C7732185',
                   'Type' : None,
                   'Digits' : '5'
                   }
    
    Units = {'TUnit' : ['K', 'F'],
             'PUnit' : ['bar', 'psia'],
             'Dunit' : ['kg%2Fm3', 'lbm%2Fft3'],
             'HUnit' : ['kJ%2Fkg', 'Btu%2Flbm'],
             'WUnit' : ['m%2Fs', 'ft%2Fs'],
             'VisUnit' : ['Pa*s', 'lbm%2Fft*s'],
             'STUnit' : ['N%2Fm', 'lb%2Fft']}
    
    params = base_params.copy()
    params['Type'] = search_type
    for key in dictionary:
        params[key] = dictionary[key]
    for key in Units:
        params[key] = Units[key][ISIMPERIAL]
    return params

def interp_calculation(LoHi, x):
    ''' SIMPLE helper function to avoid repeated interpolation calculations
    '''
    return LoHi[0] + x * (LoHi[1]-LoHi[0])

def round_sig5(x):
    ''' A function to round a value to 5 significant figures for display
    '''
    return round(eval(x), 5-int(floor(log10(abs(eval(x)))))-1)

def screen_input(x):
    ''' Screen input is the main error-prevention function in thie program.
    It first translates blank strings into NoneType for use in class initialization.
    It then also checks that the resulting inputs can be evaluated before evaluating
    them, simply returning None if it cannot be evaluated.
    '''
    if x == '':
        return None
    else:
        try:
            eval(x)
            if x == '0':
                return eval(x)
            else:
                return round_sig5(x)
        except:
            return None
    
def construct_database():
    ''' Function to initialize the database, if not already initiated.
    '''
    try:
        f = open(DB_NAME)
        f.close()
        pass
    except:
        SQLs = []
        SQLs.append("""
        CREATE TABLE IF NOT EXISTS "Cycles" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Efficiency"  REAL,
            "POut" REAL,
            "SearchTimes" INTEGER NOT NULL,
            "s1_Id"  INTEGER,
            "s2_Id"  INTEGER,
            "s3_Id"  INTEGER,
            "s4_Id"  INTEGER
        );
        """)
        SQLs.append("""
        CREATE TABLE IF NOT EXISTS 'States' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Uses' INTEGER,
          'Temp' REAL,
          'Press' REAL,
          'SpecVol' REAL,
          'Energy' REAL,
          'Enthalpy' REAL,
          'Entropy' REAL,
          'Quality' REAL,
          'Phase' TEXT,
          'Units' TEXT
        );
        """)
        database_operation(SQLs)
    pass

def database_operation(SQL_list):
    ''' Generic function to execute any LIST of SQLite commands
    and return the most recent cursor if desired.
    
    Inputs
    ------
        SQL_list : list of strings containing valid SQLite commands
    
    Returns
    -------
        A sqlite3 "cursor" object
    '''
    global DB_NAME
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    for statement in SQL_list:
        cur.execute(statement)
    conn.commit()
    return cur.fetchone()

def query_states(T, P, h, s, x):
    ''' A function to query the States table of the database,
    acting both as a cache and a way to track history of searches
    
    Inputs
    ------
        T : Temperature
        P : Pressure
        h : enthalpy
        s : entropy
        x : quality
    NOTE : only 2 can be used total to define state.
    
    Returns
    -------
        A list of attributes which can be used to override automated
        initialization of the class State.
    '''
    units = ["'metric'", "'imperial'"][ISIMPERIAL]
    select_str = '''
    SELECT Temp, Press, Enthalpy, Entropy, Quality, SpecVol, Energy, Phase, Uses
        FROM States
        WHERE %s AND %s AND Units = %s'''
    
    update_str = """
    UPDATE States
        SET Uses = %s
        WHERE %s AND %s AND Units = %s
    """
    strs = ['', '']
    count = 0
    for argument in [T, P, h, s, x]:
        if argument != None:
            count += 1
            continue
    if count != 2:
        results = None
    else:
        count = 0
        if T is not None:
            strs[count] = 'Temp = ' + str(T)
            count += 1
        if P is not None:
            strs[count] = 'Press = ' + str(P)
            count += 1
        if h is not None:
            strs[count] = 'Enthalpy = ' + str(h)
            count += 1
        if s is not None:
            strs[count] = 'Entropy = ' + str(s)
            count += 1
        if x is not None:
            strs[count] = 'Quality = ' + str(x)
            count += 1
        select_str = select_str % (strs[0], strs[1], units)   
        results = database_operation([select_str])
        if results is not None:
            uses = results[-1] + 1
            update_str = update_str % (uses, strs[0], strs[1], units)
            database_operation([update_str])
    return results

def add2database_states(S):
    ''' A function to add a state object to the database as a row
    
    Inputs
    ------
        S : A member of the class State
    
    Returns
    -------
        NONE
    '''
    global ISIMPERIAL
    Units = ["'metric'", "'imperial'"][ISIMPERIAL]
    insert_str = """
    INSERT INTO States
        VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    if S.x == None:
        X = 'NULL'
    else:
        X = str(S.x)
    if S.phase == None:
        Phase = 'NULL'
    else:
        Phase = "'" + S.phase + "'"
    insert_str = insert_str % (S.uses, S.T, S.P, S.v, S.u, S.h, S.s, X, Phase, Units)
    
    database_operation([insert_str])
    pass

def query_cycles():
    ''' Function to query the cycles table of the database.
    Not currently implemented.
    '''
    pass

def add2database_cycles():
    ''' Function to add to the cycles table in the database.
    Not currently implemented.
    '''
    pass

def open_browser():
    ''' Function to automatically open the webbrowser to the Flask App
    when run.'''
    webbrowser.open_new('http://127.0.0.1:5000/')


### FLASK APP DEFINITION ###
app = Flask(__name__)

@app.route('/')
def home():
    global STATE
    STATE = None
    return render_template('home.html', methods=['GET', 'POST'])


@app.route('/instructions/', methods=['GET', 'POST'])
def instructions():
    return render_template('instructions.html')


@app.route('/state-calculator/', methods=['GET', 'POST'])
def state_calculator():
    global ISIMPERIAL
    global STATE
    Units = [['(K)', '(bar)', '(kJ/kg)', '(J/g-K)', '(kJ/kg)'],
             ['(F)', '(psi)', '(BTU/lbm)', '(BTU/lbm-R)', '(lbm/ft3)']][ISIMPERIAL]
    reset = False
    if STATE == None:
        STATE = State()
        reset = True
    things = [STATE.T, STATE.P, STATE.h, STATE.s, STATE.x, STATE.v, STATE.u, STATE.phase]
    Values = []
    for item in things:
        if item == None:
            Values.append('')
        else:
            Values.append("Value=" + str(item))

    error_string = STATE.error
    if STATE.error == 'Errors:' or reset == True:
        error_string = ''
    
    if STATE.uses == 0:
        n_str = ''
    else:
        n_str = '(This state has been searched %s times before.)' % (STATE.uses)
    greyout = ['disabled', ''][reset]
    return render_template('state-calculator.html',
                           units=Units, vals=Values,
                           dis=greyout, err=error_string,
                           n = n_str)


@app.route('/toggle-units/', methods=['GET', 'POST'])
def toggle_units():
    global ISIMPERIAL
    global STATE
    ISIMPERIAL = not ISIMPERIAL
    STATE = None
    return redirect(url_for('state_calculator'))


@app.route('/state-clear/', methods=['GET', 'POST'])
def clear_state():
    global STATE
    STATE = None
    return redirect(url_for('state_calculator'))


@app.route('/state-results/', methods=['POST'])
def state_results():
    global STATE
    T = request.form["temperature"]
    T = screen_input(T)
    P = request.form["pressure"]
    P = screen_input(P)
    h = request.form["enthalpy"]
    h = screen_input(h)
    s = request.form["entropy"]
    s = screen_input(s)
    x = request.form["quality"]
    x = screen_input(x)
    
    db_out = query_states(T, P, h, s, x)
    if db_out is not None:
        STATE = State(ALL=db_out)
    else:
        STATE = State(T=T, P=P, h=h, s=s, x=x)
        if STATE.T != None:
            add2database_states(STATE)
    return redirect(url_for('state_calculator'))


@app.route('/cycle-calculator/', methods=['POST', 'GET'])
def cycle_calculator():
    return render_template('cycle-calculator-temporary.html')



### MAIN LOOP ###
if __name__ == '__main__':
    CACHE_DICT = open_cache()
    DB = construct_database()
    
    app.run(debug=True)



### TROUBLE-SHOOTING CODE ###    
# T = 300
# P = 60
# h = None
# s = None
# x = None

# db_out = query_states(T, P, h, s, x)
# if db_out is not None:
#     s = State(ALL=db_out)
# else:
#     s = State(T=T, P=P, h=h, s=s, x=x)
#     add2database_states(s)

# print(s.T)
# print(s.P)
# print(s.h)
# print(s.s)
# print(s.x)
# print(s.phase)
# print(s.error)

  