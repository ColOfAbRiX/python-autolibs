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
import packer
import ansible
import terraform
import configparser

class Config:
    """
    Repository Configuration
    """

    def __init__(self, repo_base):
        self._repo_base = repo_base
        self.config_file = os.path.join(self._repo_base, self.config_file())
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self.ansible = ansible.AnsibleConfig(self._repo_base)
        self.packer = packer.PackerConfig(self._repo_base)
        self.terraform = terraform.TerraformConfig(self._repo_base)

    @staticmethod
    def config_file():
        """
        Name of the configuration file
        """
        return ".repoconfig"

# vim: ft=python:ts=4:sw=4