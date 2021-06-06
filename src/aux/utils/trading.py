SHORT_POSITION = 'short'
LONG_POSITION = 'long'

def percentageChange(type, entry, exit):
    return valueChange(type, entry, exit) * 100

def valueChange(type, entry,exit):
    if type == LONG_POSITION:
        # The amount of percentage: (exit / entry - 1)* 100
        # Gain => (20/10 -1) *100= 100%
        # Loss => (10-20 -1) * 100 = -50%
        return exit / entry - 1
    elif type == SHORT_POSITION:
        # The amount of percentage gain is: (open-close)/entry => (20-10)/10 = 100%
        # The amount of percentage loss is: (close-open)/entry => (10-20)/10 = -50%
        return entry / exit  -1
