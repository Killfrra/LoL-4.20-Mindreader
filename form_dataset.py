from math import inf, sqrt
import json
import pickle
from vops import *

#data_file = 'records_0_with_champion.json'
data_file = 'records_0_same_as_0.json'

data = {}
with open(data_file) as f:
    data = json.load(f)

starts = {}
goals = {}
for id in data:
    data_id = data[id]
    positions = data_id['positions']

    type = data_id['type']
    if type != 'lane_minion':
        continue

    starts[id] = positions[0][1]
    goals[id] = positions[len(positions) - 1][1]

global_time = 0
objs = {}

"""
min_time = inf
objs_with_min_time = []
for id in data:
    obj = {}
    data_id = data[id]
    positions = data_id['positions']
    if id in objs:
        obj = objs[id]
        next_pos_idx = obj['last_pos_idx'] + 1
        if len(positions > next_pos_idx):
            next_time = positions[next_pos_idx][0]
            if next_time < min_time:
                min_time = next_time
                objs_with_min_time = []
                objs_with_min_time.append(obj)
            elif next_time == min_time:
                objs_with_min_time.append(obj)
    else:
        first_time = positions[0][0]
        if first_time > global_time:
"""

def find_next_min():
    min_id = None
    min_time = inf
    min_pos = None
    for id in data:
        data_id = data[id]

        type = data_id['type']
        if type != 'lane_minion':
            continue

        positions = data_id['positions']
        for position in positions:
            time = position[0]
            pos = position[1]
            if time > global_time and time < min_time:
                min_id = id
                min_time = time
                min_pos = pos
            #elif time == min_time:
            #    print("WARN SAME TIME")
    return (min_id, min_time, min_pos)

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

max_speed = 0

for id in data:
    data_id = data[id]
    positions = data_id['positions']

    type = data_id['type']
    if type != 'lane_minion':
        continue

    prev_time = None
    prev_pos = None
    prev_vel = None
    for position in positions:
        time = position[0]
        pos = position[1]
        if prev_pos != None:
            time_diff = time - prev_time
            #vel = vdiv(vsub(pos, prev_pos), time_diff)
            vel = vsub(pos, prev_pos)
            speed = sqrt(vlensq(vel))
            max_speed = max(speed, max_speed)
            """
            if prev_vel != None:
                acc = vsub(vel, prev_vel)
            """
            prev_vel = vel
        prev_time = time
        prev_pos = pos

print('MAX SPEED', max_speed)

#exit()

def appendXZ(l, v):
    l.append(v[0])
    l.append(v[2])

Xs = []
Ys = []

def record(obj):
    pos = obj['last_pos']
    vel = obj['last_vel']
    dvel = obj['last_dvel']

    next_vel = obj['vel']

    neighbours = get_objs_in_range(pos, radius + AvoidanceRadiusIncrease)
    #if len(neighbours) > 0:
    if True:
        X = []
        appendXZ(X, vel)
        appendXZ(X, dvel)
        for neighbor in neighbours:
            npos = neighbor['pos']
            nvel = neighbor['vel']
            rpos = vdiv(vsub(npos, pos), radius + AvoidanceRadiusIncrease)
            
            appendXZ(X, rpos)
            appendXZ(X, nvel)
        
        Y = []
        appendXZ(Y, next_vel)

        Xs.append(X)
        Ys.append(Y)

def set_dvel(obj):
    d = vsub(goals[id], obj['pos'])
    l = vlensq(d)
    if l > 0:
        #obj['dvel'] = vmul(d, speed / (l * max_speed))
        obj['dvel'] = vdiv(d, l)
        return True
    return False

prev_print_time = 0

while True:
    
    (id, time, pos) = find_next_min()
    
    if id == None:
        break
    
    global_time = time
    if (global_time - prev_print_time) > 1:
        prev_print_time = global_time
        print(global_time)

    if id in objs:
        obj = objs[id]

        obj['last_pos'] = obj['pos']
        obj['last_time'] = obj['time']
        obj['last_vel'] = obj['vel']
        obj['last_dvel'] = obj['dvel']
        obj['pos'] = pos
        obj['time'] = time
        
        #time_diff = 1 / 60 
        #time_diff = obj['time'] - obj['last_time']
        time_diff = 1

        if set_dvel(obj):
            obj['vel'] = vdiv(vsub(obj['pos'], obj['last_pos']), time_diff * max_speed)
            record(obj)
        else:
            print(id, 'reached gloal')
    else:
        obj = objs[id] = {}
        obj['id'] = id
        obj['pos'] = pos
        obj['time'] = time
        obj['vel'] = (0, 0, 0)
        set_dvel(obj)

"""
maxXY = 35 + 70

for X in Xs:
    maxXY = max(maxXY, max(X))
for Y in Ys:
    maxXY = max(maxXY, max(Y))

def norm_mat(Xs, maxx):
    for X in Xs:
        for i, x in enumerate(X, 0):
            X[i] = x / maxx

norm_mat(Xs, maxXY)
norm_mat(Ys, maxXY)
"""

maxXlen = 72
"""
for X in Xs:
    maxXlen = max(maxXlen, len(X))
"""
for X in Xs:
    while len(X) < maxXlen:
        X.append(0)

with open('output.data', 'wb') as f:
    pickle.dump((Xs, Ys), f)

with open('conditions.data', 'wb') as f:
    pickle.dump((starts, goals, max_speed), f)

with open('output.txt', 'w') as f:
    print(Xs, file=f)