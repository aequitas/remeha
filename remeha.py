#!/usr/bin/python 
import serial
import socket
import struct
import time 
import sys

from datamap import datamap, fmt

ser = serial.Serial('/dev/ttyUSB0', 
    9600, 
    timeout=0, 
    parity='N', 
    bytesize=8,
    stopbits=1
)
print 'serial open', ser.isOpen()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 8125)
print 'udp %s' % str(addr)

string = "\x02\xFE\x01\x05\x08\x02\x01\x69\xAB\x03"

def parse_data(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
        if isinstance(value, list):
            for i in zip(datamap[n][2], value, datamap[n][5]):
                if i[0]:
                    yield i
        elif datamap[n][2]:
            if value < 0:
                yield datamap[n][2], 0, datamap[n][5]
            yield datamap[n][2], value, datamap[n][5]

while True:
    sys.stdout.flush()
    ser.write(string)
    time.sleep(1)
 
    data = ser.read(ser.inWaiting())
    unpacked = struct.unpack(fmt, data)

    stats = list(parse_data(unpacked))
    for stat in stats:
        s = 'cv.{}:{}|{}'.format(*stat)
        sock.sendto(s, addr)

    assert not ser.inWaiting()
    time.sleep(3)

print 'kthxbye'
