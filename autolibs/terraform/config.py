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
import configparser

class TerraformConfig:
    """
    Packer Section Configuration
    """
    def __init__(self, repo_base):
        self._repo_base = repo_base
        self.config_file = os.path.join(self._repo_base, self.config_file())
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self._terraform = {}
        if "terraform" in self.config.sections():
            self._terraform = self.config['terraform']

    @staticmethod
    def config_file():
        return ".repoconfig"

    def base_dir(self, full_path=False):
        base_dir = self._terraform.get("base_dir", "terraform")
        if full_path:
            base_dir = os.path.join(self._repo_base, base_dir)
        return base_dir

    def environments_dir(self, full_path=False):
        environments_dir = self._terraform.get("environments_dir", "environments")
        if full_path:
            environments_dir = os.path.join(self._repo_base, environments_dir)
        return environments_dir

    def state_file(self):
        return self._terraform.get("state_file", "terraform.tfstate")

# vim: ft=python:ts=4:sw=4