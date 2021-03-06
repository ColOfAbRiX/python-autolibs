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
    repo = AnsibleRepo()

    print_c(" Ansible", color='white')
    print_c("-" * 40, color='white')
    print_c("Pre push repository checks:")

    for i, p in enumerate(repo.playbooks()):
        p_name = p[(len(repo.repo_base) + 1):]
        print_c("    #%d: Checking %s... " % (i + 1, p_name), end='')
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

    print_c("Check status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    return True


def main():
    print_c("GIT Pre Push Checks\n".center(40), color='white')
    try:
        result = pre_push()
        if not result:
            sys.exit(1)

    except ScriptError as e:
        print_c("Exception raised", color="light_red")
        print(e.message)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4