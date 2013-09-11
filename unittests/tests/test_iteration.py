
def a():
    b()

def b():
    a()
    c()

def c():
    d()

def d():
    c()
    a()
