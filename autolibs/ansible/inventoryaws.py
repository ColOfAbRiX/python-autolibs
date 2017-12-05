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

#
# Custom dynamic inventory script for Ansible that fetches instances from AWS
#
# The script scans the AWS regions for started EC2 instances and reads their
# tags to extract Ansible variables, group membership and other information. The
# script is designed to work with the other inventory script.
#
# The script uses a file named "aws_credentials" to read the AWS credentials for
# the boto3 library. The file must be present in the current working directory
# or in the same directory as this script. Also, the file must have a safe
# permissions of at least 0600.
#
# The script recognises the following tags:
#
#  Ansible: Must be set to "True" for this script to act on the instance
#
#  AnsibleName: Name assigned to the host, e.g. "amdevrabbitmq01"
#
#  AnsibleGroups: Comma separated list of the groups where the instance is a
#    member. E.g. "dev,rabbit_servers,centos_7"
#
#  AnsibleVars: A comma separates list of key/value pairs like in the following
#    example: Var1=Test Var2="Test 2", that will be added as host variables
#
#  Environment: if present, the script will add this value as a group membership
#

from __future__ import print_function

import re
import os
import boto3
import argparse
import configparser

from stat import *
from cfutils import *


def load_credentials():
    config = configparser.ConfigParser()

    # Look for the file
    aws_credentials = os.path.join(os.getcwd(), "aws_credentials")
    if not os.path.isfile(aws_credentials):
        aws_credentials = os.path.join(os.path.dirname(sys.argv[0]), "aws_credentials")
        if not os.path.isfile(aws_credentials):
            raise Exception("Cannot find file aws_credentials")

    # Ensuring strict permissions
    if os.stat(aws_credentials).st_mode & (S_IWGRP | S_IWOTH | S_IROTH):
        raise Exception("The AWS credentials files %s has unsecure permissions." % aws_credentials)
    if not os.access(aws_credentials, os.R_OK):
        raise Exception("Cannot open file aws_credentials for reading.")

    # Load and return
    config.read(aws_credentials)
    return (
        config.get('default', 'aws_access_key_id'),
        config.get('default', 'aws_secret_access_key')
    )


def build_hosts(regions=[]):
    """
    Build the lists of hosts for the inventory
    """
    instances = []

    for r in regions:
        access_key, secret_key = load_credentials()

        ec2 = boto3.resource(
            'ec2', region_name=r, aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )

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

# vim: ft=python:ts=4:sw=4