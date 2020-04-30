
def is_evaluable(x):
    try:
        eval(x)
        return(True)
    except:
        return(False)
    
test = '0'
while test != 'exit':
    print(is_evaluable(test))
    test = input('try something else! ')