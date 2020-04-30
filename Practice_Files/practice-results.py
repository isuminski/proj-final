str_list = ['', '6', '450', '', '']

var_list = ['T', 'P', 'h', 's', 'x']

for i in range(5):
    if str_list[i] == '':
        string = var_list[i] + ' = None'
        eval(string)
    else:
        string = var_list[i] + ' = ' + str_list[i]
        eval(string)




