import numpy as np

def uj2w(t,e):
    w = [(e[1]-e[0])/(t[1]-t[0])/1e6]
    for t0,t1,e0,e1 in zip(t[:-1],t[1:],e[:-1],e[1:]):
        p = (e1-e0)/(t1-t0)/1e6
        if p>100 or p<-100:
            p=0
        w.append(p)
    return np.array(w)

def sysvar(filename):
    with open(filename, 'r') as fd:
        s = fd.readline().rstrip()
        return int(s) if s.isdigit() else s
