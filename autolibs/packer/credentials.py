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


def get(raw_data, aws_region, packer_user):
    """
    Returns information about credentials to connect to AWS
    """
    result = {}

    for module in raw_data['modules']:
        for res_name, res_content in module['resources'].iteritems():
            if res_name == ("aws_iam_access_key." + packer_user):
                primary = res_content['primary']
                attributes = primary['attributes']

                result.update({
                    'aws_access_key': attributes.get('id', None),
                    'aws_secret_key': attributes.get('secret', None),
                    'aws_region': aws_region
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
    parser.add_argument(
        'aws_region',
        action='store',
        help="AWS Region."
    )
    parser.add_argument(
        'packer_user',
        action='store',
        nargs='?',
        default='packer',
        help="User used by packer."
    )
    args = parser.parse_args()

    with open(args.state_file) as data_file:
        data = json.load(data_file)

    result = get(data, args.aws_region, args.packer_user)
    print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': ')))

    sys.exit(0)

# vim: ft=python:ts=4:sw=4