#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from __future__ import print_function

import sys
import json
import argparse


def get(raw_data):
    """
    Returns information about the CentOS image to download
    """
    return {
      "image_name": "CentOS-7.3.1611-x86_64",
      "iso_url": "http://mirror.as29550.net/mirror.centos.org/7/isos/x86_64/CentOS-7-x86_64-DVD-1611.iso",
      "iso_checksum": "c455ee948e872ad2194bdddd39045b83634e8613249182b88f549bb2319d97eb"
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'state_file',
        action='store',
        default=None,
        help="Target state file."
    )
    args = parser.parse_args()

    result = get({})
    print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': ')))

    sys.exit(0)

# vim: ft=python:ts=4:sw=4