def vop1(a, func):
    if len(a) > 2:
        return (func(a[0]), func(a[1]), func(a[2]))
    else:
        return (func(a[0]), func(a[1]))

def vop2(a, b, func):
    if len(a) > 2:
        return (func(a[0], b[0]), func(a[1], b[1]), func(a[2], b[2]))
    else:
        return (func(a[0], b[0]), func(a[1], b[1]))

def vadd(a, b):
    return vop2(a, b, lambda a, b: a + b)

def vsub(a, b):
    return vop2(a, b, lambda a, b: a - b)

def vmul(a, b):
    return vop1(a, lambda a: a * b)

def vdiv(a, b):
    return vop1(a, lambda a: a / b)

def v3tov2(a):
    return (a[0], a[2])

def vlensq(d):
    if len(d) > 2:
        return d[0]**2 + d[1]**2 + d[2]**2
    else:
        return d[0]**2 + d[1]**2

def vdistsq(a, b):
    return vlensq(vsub(a, b))

def vnorm(a):
    return vdiv(a, sqrt(vlensq(a)))