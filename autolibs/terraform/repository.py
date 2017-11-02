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

from __future__ import print_function

import os
import sys
import json
import config
import argparse

from cfutils.gitutils import *

class TerraformRepo:
    """
    Information about the Terraform section of the Automation Repository
    """

    def __init__(self, repo_base=None):
        if not is_git_repo(repo_base):
            self.repo_base = None
            return

        if repo_base is None:
            repo_base = get_git_root()

        self.repo_base = repo_base
        self._config = config.TerraformConfig(self.repo_base)
        self.base = os.path.join(self.repo_base, self._config.base_dir())
        self.environments_base = os.path.join(
            self.base,
            self._config.environments_dir()
        )

    def environments(self):
        """
        The list of environments installed on Terraform
        """
        return next(os.walk(self.environments_base))[1]

    def environment_base(self, environment):
        """
        Base path of an environment
        """
        environment = os.path.join(self.environments_base, environment)

        if not os.path.exists(environment):
            raise IOError("Environment %s doesn't exist" % environment)
        if not os.path.isdir(environment):
            raise IOError("Environment %s is not a directory" % environment)

        return environment

    def state_file(self, environment):
        """
        State file of an environment
        """
        return os.path.join(
            self.environment_base(environment),
            self._config.state_file()
        )

# vim: ft=python:ts=4:sw=4