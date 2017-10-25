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

import os
import sys
import json
import argparse


def get(raw_data):
    """
    Returns information about the various configuration options for the MINIMAL
    installation
    """
    result = {}

    for module in raw_data['modules']:
        for res_name, res_content in module['resources'].iteritems():
            if res_name == "aws_s3_bucket.ami_import_bucket":
                primary = res_content['primary']
                attributes = primary['attributes']

                result.update({
                    's3_import_bucket': attributes.get('id', None)
                })

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'state_file',
        action='store',
        default=None,
        help="Target state file."
    )

    args = parser.parse_args()

    with open(args.state_file) as data_file:
        data = json.load(data_file)

    result = get(data)
    print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': ')))

    sys.exit(0)

# vim: ft=python:ts=4:sw=4