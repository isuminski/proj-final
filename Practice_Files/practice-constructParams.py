search_type = 'SatP'
dictionary = {'TLow' : 300,
            'THigh' : 300,
            'TInc' : 0}

ISIMPERIAL = False
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
print(params)



