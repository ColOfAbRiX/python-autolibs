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
import sys

from cfutils.execute import *
from cfutils.gitutils import *
from cfutils.formatting import print_c
from autolibs.ansible.repository import AnsibleRepo
from autolibs.ansible.deploy import DeployConfig


def pre_push():
    print_c("Checking push:")

    # Check we're not committing into protected branches
    print_c("  Check target branch...".ljust(38), end='')
    git_branch = re.search(r'\s*\*\s+(.*)', exec_git('branch'), re.MULTILINE).group(1).strip()
    if git_branch in ['master', 'development', 'devel']:
        print_c("ERROR", color="light_red")
        print(
            "\n"
            "PUSH ERROR - Push forbidden on protected branches"
            "\n"
            "Protected branches cannot be changed directly,\n"
            "this is bad practice that can lead to big\n"
            "problems. These branches can only be pulled from\n"
            "the remote repository.\n"
            "\n"
            "Aborting the push.\n"
        )
        return False
    print_c("OK", color='light_green')

    repo = AnsibleRepo()

    print_c("\n  GIT will now perform a syntax check of all playbooks. This might take some time.")
    print("  Found %d playbooks:" % len(repo.playbooks()))

    for i, p in enumerate(repo.playbooks()):
        print_c("    %d/%d: Checking %s... " % (i + 1, len(repo.playbooks()), p), end='')

        #
        # FIXME: This is old code and the "all" target is not meaningful anymore
        # without specifying also the environment.
        #
        #deploy = DeployConfig(repo, p, 'all', [])
        #stdout, stderr, rc = exec_cmd(deploy.deploy_full + " --syntax-check")
        #if rc != 0:
        #    print_c("ERROR", color='light_red')
        #
        #    print_c(
        #        "\nPUSH ERROR - Found syntax error while checking playbook \"%s\"" % p,
        #        color="light_red",
        #        file=sys.stderr
        #    )
        #    print(stderr)
        #    return False

        print_c("OK", color='light_green')

    print_c("Push status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    return True


def main():
    try:
        result = pre_push()
        if not result:
            sys.exit(1)
    except ScriptError as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4
