from math import log10, floor
def round_sig(x, sig=5):
    return round(eval(x), sig-int(floor(log10(abs(eval(x)))))-1)

while True:
    num = input('Number? ')
    if num == 'exit':
        break
    else:
        print(round_sig(num))