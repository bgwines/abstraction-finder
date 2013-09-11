def s():
    b()
    a()
        
def a():
    a()
    ta()

def b():
    tb()

def ta():
    pass

def tb():
    tb2()

def tb2():
    tb3()

def tb3():
    tb()
