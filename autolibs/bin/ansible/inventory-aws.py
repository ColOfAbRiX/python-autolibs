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

import re
import boto3
import argparse

from cfutils import *


def build_hosts(regions=[]):
    """
    Build the lists of hosts for the inventory
    """
    instances = []

    for r in regions:
        ec2 = boto3.resource('ec2', region_name=r)

        # Collect only instances with tag: Ansible=True
        filters = [
            {'Name': 'tag-key', 'Values': ['Ansible']},
            {'Name': 'tag-value', 'Values': ['True']},
        ]

        instances.extend(
            [build_host_info(i, r) for i in ec2.instances.filter(Filters=filters)]
        )

    return instances


def build_host_info(instance, region):
    """
    Build the information for one single host
    """
    tags = {}

    for t_key, t_value in [(t['Key'], t['Value']) for t in instance.tags]:
        tags.update({t_key: t_value})

    # Extract information from tags
    hostname = tags.get('AnsibleName', tags.get('Name', None))

    # Groups membership
    groups = tags.get('AnsibleGroups', "").split(',')
    groups.extend([region])

    # Host variables
    variables = dict(
        re.findall(r'([^=]+)=(".*?"|\S+)',
        tags.get('AnsibleVars', ""))
    )

    # Environment
    if 'Environment' in tags and tags['Environment'] not in groups:
        groups.append(tags['Environment'])

    # Additional AWS info
    variables.update({
    })

    # Build and return
    return {
        'name': hostname,
        'memberof': groups,
        'vars': variables,
    }


def build_groups(regions=[]):
    """
    Build the list of groups for the inventory
    """
    output = []
    for r in regions:
        output.append({
            'name': r,
            'description': "AWS Regions %s" % r,
            'type': 'datacenters',
            'vars': {
                'dc': r
            }
        })
    return output


def main():
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--regions', '-r',
        action='store',
        nargs='?',
        default="",
        help="List of regions where to run the inventory."
    )
    args = parser.parse_args()

    # Find the list of regions
    regions = filter(None, args.regions.lower().split(','))
    if not regions:
        regions = [x['RegionName'] for x in boto3.client('ec2').describe_regions()['Regions']]

    # Extract the information
    output = {
        'hosts': build_hosts(regions=regions),
        'groups': build_groups(regions=regions),
        'vars': {
            'aws': True
        }
    }

    p_json(output)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4