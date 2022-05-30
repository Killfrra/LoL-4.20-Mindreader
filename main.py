import json
import numpy as np
from math import sin, cos, sqrt
import matplotlib.pyplot as plt

def rotate(v, angle):
    angle = np.deg2rad(angle)
    c = cos(angle)
    s = sin(angle)
    return (
        v[0] * c - v[1] * s,
        v[1] * c + v[0] * s
    )

def diff(a, b):
    return (
        a[0] - b[0],
        a[1] - b[1]
    )

def div(a, b):
    return (
        a[0] / b,
        a[1] / b
    )

def mul(a, b):
    return (
        a[0] * b,
        a[1] * b
    )

def len2(v):
    return sqrt((v[0] * v[0]) + (v[1] * v[1]))

records = {}
fname = 'visualizer/records_0_same_as_0.json'
with open(fname, 'r') as input:
    print('loading...')
    records = json.load(input)
    print('loaded')

prev_time = None
prev_pos = None
prev_vel = None
dx = []
dy = []
positions = records['1073745689']['positions']

for i, (time, pos) in enumerate(positions):
    #if i < len(positions) - 1 and i % 1 == 0:
    pos = (pos[0], pos[2])
    if prev_pos != None:
        time_diff = time - prev_time
        if time_diff <= 0:
            continue
        vel = div(diff(pos, prev_pos), time_diff)
        if prev_vel != None:
            acc = div(diff(vel, prev_vel), time_diff)
            dx.append(time)
            #dy.append(pos)
            #dy.append(vel)
            #dy.append(time_diff)
            dy.append(acc)
        prev_vel = vel
    prev_time = time
    prev_pos = pos

#print([*zip(dx, dy)])

plt.plot(dx, dy)
plt.show()
