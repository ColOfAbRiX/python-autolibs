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
from autolibs.config import Config
from autolibs.repository import RepoInfo
from ansible import prepush as ansible


def pre_push():

    print_c(" Repository", color='white')
    print_c("-" * 40, color='white')
    print_c("Pre push repository checks:")

    # Check we're not committing into protected branches
    print_c("  Target branch...", end='')
    git_branch = re.search(r'\s*\*\s+(.*)', exec_git('branch'), re.MULTILINE).group(1).strip()
    if git_branch in ['master', 'development', 'devel']:
        print_c("ERROR", color="light_red")
        print(
            "\nPush forbidden on protected branches\n\n"
            "Protected branches cannot be changed\n"
            "directly, this is bad practice that can\n"
            "lead to big problems. These branches\n"
            "can only be pulled from the remote\n"
            "repository.\n\n"
            "Aborting the push.\n"
        )
        return False
    print_c("OK", color='light_green')

    print_c("Check status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    try:
        config = Config(RepoInfo().repo_base)

        # Ansible GIT hook
        if os.path.isdir(config.ansible.base_dir(full_path=True)):
            if not ansible.pre_push():
                sys.exit(1)

    except ScriptError as e:
        print_c("Exception raised", color="light_red")
        print(e.message)
        sys.exit(1)

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