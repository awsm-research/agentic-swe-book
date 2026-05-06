def proc(d, f, x):
    r = []
    for i in d:
        if i[2] == 1:
            if f:
                r.append(i)
            elif i[3] <= x:
                r.append(i)
    return r
