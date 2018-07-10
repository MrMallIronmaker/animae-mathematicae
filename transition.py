from math import cos, sin, pi, sqrt, tan, atan2

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

class Arc:
    def __init__(s, start_pos, end_pos, arc, sec):
        # calculate center, radius, and start and end rads.
        if (arc == 0):
            raise ValueError("Arc can't be zero - for that, use a linear transition.")
        if (arc >= 2 * pi):
            raise ValueError("Arc greater than 2pi isn't implemented.");
            
        s.center = (
            (end_pos[0] + start_pos[0])/2. + (start_pos[1] - end_pos[1])/2. / tan(arc/2.),
            (end_pos[1] + start_pos[1])/2. + (end_pos[0] - start_pos[0])/2. / tan(arc/2.)
        )
        
        s.radius = sqrt(
            (end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2
        )/2. / abs(sin(arc/2.))
        
        theta_s = atan2(start_pos[1] - s.center[1], start_pos[0] - s.center[0])
        theta_e = atan2(end_pos[1] - s.center[1], end_pos[0] - s.center[0])
        
        def close(a, b):
            assert abs(a - b) < 0.001, "{} and {} are not close".format(a, b)
        
        close(start_pos[0], s.center[0] + s.radius * cos(theta_s))
        close(start_pos[1], s.center[1] + s.radius * sin(theta_s))
        close(end_pos[0], s.center[0] + s.radius * cos(theta_e))
        close(end_pos[1], s.center[1] + s.radius * sin(theta_e))
        
        
        if arc - 0.01 > theta_e - theta_s:
            theta_e += 2*pi
        elif arc + 0.01 < theta_e - theta_s:
            theta_s += 2*pi
            
        close(arc, theta_e - theta_s)
        
        s.rad = Cosine(
            theta_s,
            theta_e,
            sec
        )
        
    def __call__(s, t):
        rad = s.rad(t)
            
        cx, cy = s.center
        
        return (cx + s.radius * cos(rad), cy + s.radius * sin(rad))
        
        
        
        
        
        