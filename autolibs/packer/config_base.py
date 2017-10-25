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


def get(raw_data, environment):
    """
    Returns information about the various configuration options for the BASE
    installation
    """
    result = {}

    security_groups = []
    for module in data['modules']:
        for res_name, res_content in module['resources'].iteritems():
            primary = res_content['primary']
            attributes = primary['attributes']

            if res_name == "aws_security_group.outbound_all":
                security_groups.append(attributes['id'])
            if res_name == "aws_security_group.inbound_all":
                security_groups.append(attributes['id'])
            if res_name == "aws_vpc.default":
                vpc_id = attributes['id']
            if res_name == "aws_subnet.tier_2.0":
                subnet_id = attributes['id']

    result.update({
        'security_group_ids': ",".join(security_groups),
        'vpc_id': vpc_id,
        'subnet_id': subnet_id,
        'environment': environment
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
        'environment',
        action='store',
        default=None,
        help="Target environment."
    )
    args = parser.parse_args()

    with open(args.state_file) as data_file:
        data = json.load(data_file)

    result = get(data, args.environment)
    print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': ')))

    sys.exit(0)

# vim: ft=python:ts=4:sw=