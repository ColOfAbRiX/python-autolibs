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
#

from __future__ import print_function

import re
import os
import sys
import yaml

from cfutils.common import *
from cfutils.gitutils import *
from cfutils.formatting import print_c
from autolibs.ansible.repository import AnsibleRepo


def pre_commit():
    repo = AnsibleRepo()

    print_c(" Ansible", color='white')
    print_c("-" * 40, color='white')
    print_c("Commit repository checks:")

    # Check YAML syntax (not Ansible validity, it will take too long)
    print_c("  Checking YAML syntax... ", end='')
    bad_yaml = []
    for root, _, files in os.walk(repo.base, topdown=False):
        if '.git' in root:
            continue
        for name in files:
            name = os.path.join(root, name)
            if not is_valid_yaml(name):
                bad_yaml.append(name)

    if len(bad_yaml) > 0:
        print_c("ERROR", color='light_red')
        print(
            "\nBad YAML syntax\n\n"
            "Some YAML files were found having a bad\n"
            "syntax. It's not possible to commit \n"
            "incorrect files.\n\n"
            "Bad files:"
        )
        for f in bad_yaml:
            print("  %s" % f[(len(repo.base) + 1):])
        print(
            "\nAborting the commit.\n"
        )
        return False

    print_c("OK", color='light_green')

    # Check cleartext passwords
    print_c("  Checking cleartext secrets... ", end='')
    vaults = []
    for root, _, files in os.walk(repo.base, topdown=False):
        if '.git' in root:
            continue
        for name in files:
            name = os.path.join(root, name)
            if contains_cleartext_secrets(name):
                vaults.append(name)

    if len(vaults) > 0:
        print_c("ERROR", color='light_red')
        print(
            "\nClear text secrets\n\n"
            "The following files need to be\n"
            "encrypted before it's possibile to\n"
            "commit. Storing a clear text password\n"
            "or SSH/SSL private keys in GIT is\n"
            "really unsecure!\n\n"
            "Only the value \"Passw0rd\" is allowed\n"
            "as a default password in cleartext.\n\n"
            "Sensitive files:"
        )
        for f in vaults:
            print("  %s" % f[(len(repo.base) + 1):])
        print(
            "\nAborting the commit.\n"
        )
        return False

    print_c("OK", color='light_green')
    print("Check status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    return True


def is_valid_yaml(filename):
    """
    Checks if a filename is a valid YAML file
    """
    if not re.findall(r'\.ya?ml$', filename, re.IGNORECASE):
        return True

    if not os.access(filename, os.R_OK):
        return True

    try:
        with open(filename, "r") as f:
            for a in yaml.safe_load_all(f):
                pass
    except yaml.YAMLError:
        return False

    return True


def contains_cleartext_secrets(filename):
    """
    Checks if any password variable is left cleartext, except for default passwords
    """
    if not os.access(filename, os.R_OK):
        return False

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue

            # Check for passwords
            if re.search(r'\S?(passwords?|passwd|pwd|_pass):\s*\w+', line, re.IGNORECASE):
                # Relevant only in YAML files, where we set variables
                if not filename.lower().endswith('.yml'):
                    continue

                password = re.findall(r':\s*(.*)$', line, re.IGNORECASE)

                # We allow only the default password...
                if password[0] == 'Passw0rd':
                    continue
                # ...as well as boolean values
                if password[0].lower() in ['false', 'true']:
                    continue

                return True

            # Check for private keys
            if re.search(r'-----.*PRIVATE KEY-----', line):
                if filename.lower().endswith('.py') or \
                   filename.lower().endswith('access_key.pem'):
                    continue

                return True

    return False


def main():
    print_c("GIT Pre Commit Checks\n".center(40), color='white')
    pre_commit()


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4