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
# deploy-support.py - Support script to provide autocompletion for the deploy script
#

from __future__ import print_function

import re
import sys
import glob
import argparse

from cfutils.execute import *
from autolibs.ansible.deploy import DeployConfig
from autolibs.ansible.repository import AnsibleRepo


def ansible_playbook_options():
    """
    Lists the options available  for ansible-playbook
    """
    ansible_options = [
        "--ask-become-pass", "--ask-pass", "--ask-su-pass", "--ask-sudo-pass",
        "--ask-vault-pass", "--become", "--become-method", "--become-user",
        "--check", "--connection", "--diff", "--extra-vars", "--flush-cache",
        "--force-handlers", "--forks", "--help", "--inventory-file", "--key-file",
        "--limit", "--list-hosts", "--list-tags", "--list-tasks", "--module-path",
        "--new-vault-password-file", "--output", "--private-key",
        "--scp-extra-args", "--sftp-extra-args", "--skip-tags",
        "--ssh-common-args", "--ssh-extra-args", "--start-at-task", "--step",
        "--su", "--su-user", "--sudo", "--sudo-user", "--syntax-check", "--tags",
        "--timeout", "--user", "--vault-password-file", "--verbose", "--version",
        "-b", "-C", "-c", "-D", "-e", "-f", "-h", "-i", "-k", "-K", "-l", "-M",
        "-R", "-s", "-S", "-t", "-T", "-u", "-U", "-v", "-vv", "-vvv", "-vvvv"
    ]

    custom_options = [
        "--skip-signature"
    ]

    return ansible_options + custom_options


def list_playbooks(repo_info):
    """ It relies on the AnsibleRepo object to list the playbooks. """
    repo_info = AnsibleRepo()
    return [os.path.relpath(p, repo_info.playbooks_base) for p in repo_info.playbooks()]


def list_environments(repo_info, playbook):
    """ List what's available in the inventory path. """
    file_list = glob.glob(paths_full(repo_info.repo_base, repo_info.inventory_base, "*"))
    return [os.path.basename(f) for f in file_list]


def list_host_groups(repo_info, playbook, target):
    """ List the hosts and groups available in the repository. """
    deploy_info = DeployConfig(repo_info, playbook, target, "")

    stdout, stderr, rc = exec_cmd("%s --list-hosts=name --list-groups=name" % deploy_info.inventory)
    if rc > 0:
        sys.exit(0)

    return sorted(stdout.split('\n'))


def list_tags(repo_info, playbook, target):
    """ It lists the Ansible tags in the repository. """
    return repo_info.tags()


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
    except ScriptError:
        sys.exit(0)

    # Don't output anything if we're not in a repository
    if repo_info.repo_base is None:
        return

    # First parameter, playbook
    if args.current_word == 1:
        result = list_playbooks(repo_info)

    # Second parameter, environment
    elif args.current_word == 2:
        playbook = args.words[1]
        result = list_environments(repo_info, playbook)

    # From third on, filter or ansible arguments
    elif args.current_word >= 3:
        playbook, environment = args.words[1:3]
        previous_word = args.words[args.current_word - 1]
        current_word = args.words[args.current_word]

        if previous_word in ['-t', '--tags', '--skip-tags']:
            result = list_tags(repo_info, playbook, environment)

        elif previous_word in ['-l', '--limit']:
            result = list_host_groups(repo_info, playbook, environment)

        else:
            result = ansible_playbook_options()

            # The third parameter can also be the target
            if args.current_word == 3:
                result += list_host_groups(repo_info, playbook, environment)

    # Output
    print('\n'.join(result))

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4