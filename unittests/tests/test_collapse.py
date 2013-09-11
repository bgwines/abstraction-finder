def f():
    g()
    t()

def g():
    h()

def h():
    f()
    z()

def s():
    f()

def t():
    pass

def z():
    pass
