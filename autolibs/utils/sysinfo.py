#!/usr/bin/env python
#
# MIT License
#
# Copyright (c) 2017 Fabrizio Colonna <colofabrix@tin.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function
import crypt
import fcntl
import socket
import struct


def network_info():
    """ Retrieves the network configuration of the host """
    output = {'ip': '127.0.0.1', 'netmask': '255.0.0.0', 'iface': '', 'gateway': ''}

    # Default interface and gateway
    with open("/proc/net/route") as f:
        for line in f.readlines():
            try:
                iface, dest, gateway, flags, _, _, _, _, _, _, _, =  line.strip().split()
                if dest != '00000000' or not int(flags, 16) & 2:
                    continue
                output['iface'] = iface
                output['gateway'] = socket.inet_ntoa(struct.pack("<L", int(gateway, 16)))
            except:
                continue

    # IP Address and netmask
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        output['ip'] = s.getsockname()[0]
        output['netmask'] = socket.inet_ntoa(fcntl.ioctl(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
            35099,
            struct.pack('256s', output['iface'])
        )[20:24])
    finally:
        s.close()

    return output

# vim: ft=python:ts=4:sw=4