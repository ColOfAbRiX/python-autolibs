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

import os
import sys

from cfutils.execute import *
from cfutils.formatting import *
from autolibs.config import Config
from packer import precommit as packer
from autolibs.repository import RepoInfo
from ansible import precommit as ansible
from terraform import precommit as terraform


def pre_commit():
    print_c(" Repository", color='white')
    print_c("-" * 40, color='white')

    print_c("Pre commit repository checks: ", end='')
    print_c("OK", color='light_green')

    print_c("Check status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    # We make calls to sub-checks for each component so that there can be
    # specific checks for Ansible, Terraform and Packer
    try:
        config = Config(RepoInfo().repo_base)

        # Ansible GIT hook
        if os.path.isdir(config.ansible.base_dir(full_path=True)):
            if not ansible.pre_commit():
                sys.exit(1)

        # Packer GIT hook
        if os.path.isdir(config.packer.base_dir(full_path=True)):
            if not packer.pre_commit():
                sys.exit(1)

        # Terraform GIT hook
        if os.path.isdir(config.terraform.base_dir(full_path=True)):
            if not terraform.pre_commit():
                sys.exit(1)

    except ScriptError as e:
        print_c("Exception raised", color="light_red")
        print(e.message)
        sys.exit(1)

    sys.exit(0)


def main():
    print_c("GIT Pre Commit Checks\n".center(40), color='white')
    pre_commit()


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4