#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2017 - Fabrizio Colonna <colofabrix@tin.it>
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
# vault - Wrapper for ansible-vault
#

from __future__ import print_function


import os
import re
import sys
import argparse

from cfutils.common import *
from cfutils.execute import exec_cmd
from cfutils.formatting import print_c
from autolibs.ansible.repository import AnsibleRepo


def get_debuglevel(ansible_args):
    """
    Discover and return the debug level
    """
    debug_level = 0
    debugging = [x for x in ansible_args if x.startswith('-v')]

    if len(debugging) > 0:
        debug_level = debugging[0].count('v')

    if debug_level > 0:
        print_c("Verbose mode #%d" % debug_level, "cyan")

    return debug_level


def vault(valut_type, action, environment, target, kwargs):
    try:
        repo_config = AnsibleRepo()
    except (ValueError, IOError, LookupError) as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    debug_level = get_debuglevel(kwargs)
    search_base = os.path.join(repo_config.base, repo_config.inventory_base, environment)

    vault_cmd = "%s %s" % (repo_config.ansible_vault, action)
    vault_file = os.path.join(search_base, repo_config.vault_file)

    # Look for vault file
    if os.path.isfile(vault_file):
        vault_cmd += " --vault-password-file=%s" % vault_file
    else:
        vault_cmd += " --ask-vault-pass"

    # Build path of the target
    if valut_type == 'host':
        target_path = "host_vars"
    elif valut_type == 'group':
        target_path = "group_vars"
    target_path = os.path.join(search_base, target_path)
    target_path = os.path.join(target_path, target)
    target_path = "%s/secrets.yml" % target_path

    # Checks based on the selected action
    if action in ['encrypt', 'decrypt']:
        if not os.path.isfile(target_path):
            raise ScriptError("Can't find the target file \"%s\"" % target_path)

    vault_cmd += " \"%s\"" % target_path

    # Any additional argument
    vault_cmd += " " + ' '.join(kwargs)

    if debug_level > 0:
        print("Executing: %s" % vault_cmd)

    # Execute
    stdout, stderr, rc = exec_cmd(vault_cmd.strip())
    if rc != 0:
        print_c(stderr, color="light_red")
    else:
        print("Done")
        os.chmod(target_path, 0664)
    exit(rc)


def main():
    print_c("Ansible Vault Wrapper\n", color="white")

    parser = argparse.ArgumentParser()

    # This command can work differently based on its name.
    match = re.search(r'-(\w+)$', sys.argv[0])
    if match is None:
        parser.add_argument(
            "vault_type",
            choices=['host', 'group'],
            help="What type of vault action to peform."
        )
        vault_type = None
    else:
        vault_type = match.group(1)

    # Arguments
    parser.add_argument(
        "vault_action",
        choices=['create', 'decrypt', 'edit', 'encrypt', 'rekey', 'view'],
        help="Vault action"
    )
    parser.add_argument(
        "environment",
        help="The environment to target."
    )
    parser.add_argument(
        "target",
        help="The group or host target."
    )
    parser.add_argument(
        "ansible",
        nargs='*',
        help="These options will be passed directly to Ansible as they are."
    )

    args, others = parser.parse_known_args()

    # If the type cannot be determined using the exec name, then check for the argument
    if vault_type is None:
        vault_type = args.vault_type

    try:
        vault(vault_type, args.vault_action, args.environment, args.target, others)

    except ScriptError as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4