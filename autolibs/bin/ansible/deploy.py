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
# deploy - Wrapper for ansible-playbook and deployment management
#

from __future__ import print_function

import sys
import shlex
import textwrap
import argparse

from cfutils.execute import *
from cfutils.formatting import print_c
from autolibs.ansible.deploy import DeployConfig
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


def deploy(args, ansible_args):
    # Getting information about the repository and the deployment
    repo = AnsibleRepo()

    if repo.repo_base is None:
        print_c("ERROR: ", color="light_red", end='')
        print("The current directory is not a GIT repository.")
        sys.exit(1)

    deploy = DeployConfig(repo, args.playbook, args.target, args.filter, ansible_args)
    debug_level = get_debuglevel(ansible_args)

    # Warn the user that vault is being used
    if len(repo.vaulted()) > 0 and debug_level > 0:
        print_c("Found encrypted files, vault password needed.", color="yellow")
        if deploy.vault_file:
            print_c("Vault password found in: \"%s\"." % deploy.vault_file, color="green")

    env = {}

    # Warn the user we're in check mode
    if '--check' in ansible_args:
        print_c("Running in check mode. No changes and no signature.", color="light_green")
        env['ANSIBLE_DEPLOY_SKIP_PLAYBOOK'] = args.playbook

    # If requested, disable the signature for this playbook
    if args.skip_signature:
        print_c("No signature will be written.", color="white")
        env['ANSIBLE_DEPLOY_SKIP_PLAYBOOK'] = args.playbook

    # Deploy! Yay!
    ans_pid = os.fork()
    if ans_pid == 0:
        # The deployment is done on a forked process so it can share the same variables, its
        #  output can be visualized and the return code caught.
        print_c("Execution started...", color="white")
        if debug_level > 0:
            command = shlex.split(deploy.deploy_full)
            print_c("  Executing: %s" % command[0], color="cyan")
            print_c('\n'.join(["    %s" % x for x in command[1:]]), color="cyan")
            if repo.run_as is not None and repo.run_as != getpass.getuser():
                print_c("  Running Ansible as user \"%s\"." % repo.run_as, color="cyan")

        # Run Ansible on a separate process
        switch_cmd(
            deploy.deploy_full,
            run_as=repo.run_as,
            cwd=repo.repo_base,
            env=env
        )
    else:
        # Wait for the above process until it has finished
        _, status = os.waitpid(ans_pid, 0)
        if status > 0:
            sys.exit(1)


def main():
    print_c("Ansible Deployment Wrapper v2.2.1\n", color="white")

    parser = argparse.ArgumentParser(
        description="Wrapper for ansible-playbook and deployment management.",
        epilog='\n'.join([
            "Notes:",
            "  All relative paths refers to the root of the GIT repository where all the",
            "  code must reside.",
            "",
            "Other features:",
            "",
            "  The script can use a password file to decrypt vaulted files. The file must",
            "  reside in the repository root, be named vault.txt and contain only the vault",
            "  password. The vault file should be present inside .gitignore and it is",
            "  recommended to use secure permission '0400'.",
            "",
            "  The script can use Ansible dynamic inventories. If it finds the script, it",
            "  will invoke Ansible with it instead of an inventory file and the chosen",
            "  environment will become a filter on groups.",
            "",
            "  See ansible.cfg, section \"repository\" for more information.",
            "",
        ]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--skip-signature',
        action='store_true',
        help="If present, it will skip the writing and updating of the deployment signature."
    )
    parser.add_argument(
        'playbook',
        help="Name of the Ansible Playbook found anywhere in the playbooks directory."
    )
    parser.add_argument(
        'target',
        help="Target of the run. It can be a usual Ansible inventory or an executable file as dynamic inventory; if a "
             "relative path then it will be searched in various default locations.",
    )
    parser.add_argument(
        'filter',
        help="An Ansible pattern that will be used to further filter the target hosts, it's equivalent to the Ansible "
             "-l option.",
        nargs="?"
    )
    parser.add_argument(
        'ansible',
        nargs='*',
        help="These options will be passed, as they are, directly to Ansible."
    )
    args, others = parser.parse_known_args()

    try:
        deploy(args, others)
        sys.exit(0)

    except ScriptError as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4