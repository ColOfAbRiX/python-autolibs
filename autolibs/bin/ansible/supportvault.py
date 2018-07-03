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
# deploy-support.py - Support script to provide autocompletion for the deploy script
#

from __future__ import print_function

import os
import re
import sys
import argparse

from autolibs.utils.common import *
from autolibs.utils.execute import *
from autolibs.utils.formatting import print_c
from autolibs.ansible.deploy import DeployConfig
from autolibs.ansible.repository import AnsibleRepo


def list_actions():
    """ Lists the actions available. """
    return [
        "create", "decrypt", "edit", "encrypt", "rekey", "view"
    ]


def list_environments(repo_info):
    """ List what's available in the inventory path. """
    return os.listdir(
        paths_full(repo_info.base, repo_info.inventory_base)
    )


def list_hosts(inventory_base, environment):
    """ List the available hosts in the host_vars directory. """
    return os.listdir(
        paths_full(inventory_base, environment, "host_vars")
    )


def list_groups(inventory_base, environment):
    """ List the available hosts in the group_vars directory. """
    return os.listdir(
        paths_full(inventory_base, environment, "group_vars")
    )


def known_arguments(args):
    """ Returns a dictionary with the arguments that the user already filled """
    return {
        'command':     args.words[0] if len(args.words) > 0 else None,
        'action':      args.words[1] if len(args.words) > 1 else None,
        'environment': args.words[2] if len(args.words) > 2 else None,
        'target':      args.words[3] if len(args.words) > 3 else None
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'current_word',
        action='store',
        type=int,
        help="Index of the current word being edited."
    )
    parser.add_argument(
        'words',
        action='store',
        nargs='*',
        help="List of all the words in the command line."
    )

    args = parser.parse_args()

    result = []
    try:
        repo_info = AnsibleRepo()
    except (ValueError, IOError, LookupError) as e:
        sys.exit(1)
    except ScriptError:
        sys.exit(0)

    # Don't output anything if we're not in a repository
    if repo_info.base is None:
        return

    inventory_base = paths_full(repo_info.base, repo_info.inventory_base)

    known = known_arguments(args)
    try:
        target_type = re.search(r'-(\w+)$', known['command']).group(1)
    except AttributeError:
        target_type = ''

    # First parameter, action
    if args.current_word == 1:
        result = list_actions()

    # Second parameter, environment
    elif args.current_word == 2:
        result = list_environments(repo_info)

    # Third parameter, target
    elif args.current_word == 3:

        if target_type == 'host':
            result = list_hosts(inventory_base, known['environment'])

        elif target_type == 'group':
            result = list_groups(inventory_base, known['environment'])

    # Output
    print('\n'.join(result))

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4