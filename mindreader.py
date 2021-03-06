import sys
import os
import struct
import json
import signal
import select
import traceback
import time as time_lib

sys.path.append('/usr/share/gameconqueror')
from consts import LIBDIR
from GameConqueror import GameConqueror
from backend import GameConquerorBackend

gc = type('',(object,),{
    'backend': None,
    'command_lock': type('',(object,),{
        'acquire': lambda self: None,
        'release': lambda self: None
    })()
})()

plist = GameConqueror.get_process_list(gc)

pid = None
for p in plist:
    if 'League of Legends.exe' in p[2]:
        pid = p[0]
        break

if pid == None:
    print('Process not found')
    exit()

backend = gc.backend = GameConquerorBackend(os.path.join(LIBDIR, 'libscanmem.so.1'))
backend.send_command('pid %d' % (pid,))

def read_value(format, addr, offset = 0):
    data = GameConqueror.read_memory(gc, addr + offset, struct.calcsize(format))
    if data == None:
        return None
    return struct.unpack(format, data)

wine32 = int('400000', 16)
om_addr = int('1D10A34', 16) + wine32
gc_addr = int('29791A8', 16) + wine32
gc_time_addr = read_value('I', gc_addr)[0] + int('2c', 16)
pos_offset = int('60', 16)
id_offset = int('FC', 16)
# if   0CFF31E8 <- champion
# then 0CFFEF30 <- dir?

records = {}

def create(id, type):
    if id not in records:
        records[id] = {}
    records[id]['type'] = type

def add_pos(id, time, pos):
    if id not in records:
        records[id] = { 'positions': [ (time, pos) ] }
    else:
        obj = records[id]
        if 'positions' not in obj:
            obj['positions'] = [ (time, pos) ]
        else:
            positions = obj['positions']
            last_index = len(positions) - 1
            last_time, last_pos = positions[last_index]
            if time == last_time: #or (pos == last_pos and last_index != 0):
                positions[last_index] = (time, pos)
            elif pos != last_pos:
                positions.append((time, pos))

exited = False # For some reason, exit() calls SIGINT
def int_handler(sig=None, frame=None):
    global exited
    if not exited:
        exited = True

        with open('records.json', 'w') as output:
            output.write(json.dumps(records, indent=4))
        
        print('Saved')

        backend.exit_cleanup()
        exit()

signal.signal(signal.SIGINT, int_handler)

print('Reading...')

mask2type = {
    17373484: 'lane_minion',
    17376776: 'champion'
}

try:
    while True:

        time = read_value('f', gc_time_addr)[0] #time_lib.time()
        obj_list_first_el_addr, obj_list_last_el_addr = read_value('II', om_addr)

        if obj_list_first_el_addr != 0 and obj_list_last_el_addr != 0:
            for addr in range(obj_list_first_el_addr, obj_list_last_el_addr, 4):
                
                unit_addr = read_value('I', addr)
                # if unit_addr == None:
                #     print('unit_addr at', addr, 'is undefined')
                #     break
                unit_addr = unit_addr[0]
                                    
                id = read_value('I', unit_addr, id_offset)
                # if id == None:
                #     print('id at', unit_addr, 'is undefined')
                #     break
                id = id[0]

                if id not in records:
                    mask = read_value('I', unit_addr)
                    # if mask == None:
                    #     print('mask at', unit_addr, 'is undefined')
                    #     break
                    mask = mask[0]

                    type = mask2type.get(mask, 'unknown')
                    create(id, type)

                pos = read_value('fff', unit_addr, pos_offset)
                pos = pos + read_value('fff', unit_addr, int('18e0', 16))
                pos = pos + read_value('fff', unit_addr, int('1900', 16))
                # if pos == None:
                #     print('pos at', unit_addr, 'is undefined')
                #     break

                add_pos(id, time, pos)

        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            int_handler()
            break

        #time.sleep(1 / 60)

except Exception:
    traceback.print_exc()
    int_handler()

"""
sub_617390
"""