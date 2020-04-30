ISIMPERIAL = False

def State(self, T=None, P=None, v=None, u=None, h=None, s=None, Sat=False, Phase=None):
    
    global ISIMPERIAL
    Units = {'TUnit' : ['K', 'F'],
             'PUnit' : ['bar', 'psia'],
             'Dunit' : ['kg%2Fm3', 'lbm%2Fft3'],
             'HUnit' : ['kJ%2Fkg', 'Btu%2Flbm'],
             'WUnit' : ['m%2Fs', 'ft%2Fs'],
             'VisUnit' : ['Pa*s', 'lbm%2Fft*s'],
             'STUnit' : ['N%2Fm', 'lb%2Fft']}
    