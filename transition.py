from math import cos, pi

def mul(f, val):
    if type(val) == tuple:
        # interpret as coordinates
        return tuple([f * v for v in val])
    else:
        return f * val

            
def add(val1, val2):
    if type(val1) == tuple and type(val2) == tuple:
        # interpret as coordinates
        return tuple([a + b for a, b in zip(val1, val2)])
    else:
        return val1 + val2

            
class Linear:
    def __init__(s, start, stop, sec):
        s.start = start
        s.stop = stop
        s.sec = sec
        s.t_0 = None
                          
        
    def __call__(s, t):
        if s.t_0 is None:
            s.t_0 = t
            
        if t - s.t_0 < 0:
            return s.start
        elif t - s.t_0 > s.sec:
            return s.stop
        else:
            progression = (t - s.t_0) / float(s.sec)
            result = add(
                mul(progression, s.stop),
                mul(1 - progression, s.start)
            )
            return result

class Constant:
    def __init__(s, val, time=None):
        s.val = val
        s.time = time
    
    def __call__(s, t):
        return s.val

# TODO: make this a lot more extensible
class Cosine:
    def __init__(s, start, stop, sec):
        s.start = start
        s.stop = stop
        s.sec = sec
        s.t_0 = None
                          
        
    def __call__(s, t):
        if s.t_0 is None:
            s.t_0 = t
            
        if t - s.t_0 < 0:
            return s.start
        elif t - s.t_0 > s.sec:
            return s.stop
        else:
            # note that this is the only line that changes
            progression = (1 - cos(pi * (t - s.t_0) / float(s.sec))) / 2
            
            result = add(
                mul(progression, s.stop),
                mul(1 - progression, s.start)
            )
            return result