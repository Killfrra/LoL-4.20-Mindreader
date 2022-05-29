import json
from math import sqrt
import pickle
from vops import *

starts = {}
goals = {}
max_speed = 0
with open('conditions.data', 'rb') as f:
    starts, goals, max_speed = pickle.load(f)

objs = {}
data = {}
for id in starts:
    obj = objs[id] = {}
    obj['pos'] = starts[id]
    obj['vel'] = (0, 0, 0)

    #print(starts[id], goals[id])

    data[id] = {
        'type': 'lane_minion',
        'positions': []
    }

regr = None
with open('regressor.data', 'rb') as f:
    regr = pickle.load(f)

#TODO: deduplicate
def get_objs_in_range(pos, range):
    ret = []
    for obj in objs.values():
        dist = vdistsq(obj['pos'], pos)
        if dist != 0 and dist < range ** 2:
            ret.append(obj)
    return ret

radius = 35.744
AvoidanceRadiusIncrease = 70
speed = 325.0

def appendXZ(l, v):
    l.append(v[0])
    l.append(v[2])

global_time = 0
time_delta = 1 / 60
for frame in range(900):

    global_time += time_delta
    
    for id, obj in objs.items():
        pos = obj['pos']
        vel = obj['vel']

        d = vsub(goals[id], pos)
        l = vlensq(d)
        if l < 0.1:
            vel = (0, 0, 0)
        else:
            #dvel = vmul(d, speed / (sqrt(l) * max_speed))
            dvel = vdiv(d, sqrt(l))

            neighbours = get_objs_in_range(pos, radius + AvoidanceRadiusIncrease)
            
            """
            if len(neighbours) == 0:
                vel = dvel
            else:
            """
            if True:
                X = []
                appendXZ(X, vel)
                appendXZ(X, dvel)
                for neighbor in neighbours:
                    npos = obj['pos']
                    nvel = obj['vel']
                    rpos = vdiv(vsub(npos, pos), radius + AvoidanceRadiusIncrease)
                    
                    appendXZ(X, rpos)
                    appendXZ(X, nvel)

                while len(X) < 72:
                    X.append(0)

                pvel = regr.predict([X])[0]
                vel = (pvel[0], 0, pvel[1])
            #"""

        #pos = vadd(pos, vmul(vel, max_speed * time_delta))
        pos = vadd(pos, vmul(vel, max_speed))

        obj['pos'] = pos
        obj['vel'] = vel

        data[id]['positions'].append((global_time, pos))

with open('predicted.json', 'w') as f:
    f.write(json.dumps(data, indent=4))