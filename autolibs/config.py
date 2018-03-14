#!/usr/bin/env python
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
        if not os.path.isdir(repo_base):
            raise ValueError("Not a valid path: %s" % repo_base)
        self._repo_base = repo_base

        self.config_file = os.path.join(self._repo_base, self.config_file())
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if "repository" not in self.config.sections():
            self.config = None
            self._repository = None
        else:
            self._repository = self.config['repository']

        # Ansible
        try:
            self.ansible = ansible.AnsibleConfig(self._repo_base)
        except LookupError:
            self.ansible = None

        # Packer
        try:
            self.packer = packer.PackerConfig(self._repo_base)
        except LookupError:
            self.packer = None

        # Terraform
        try:
            self.terraform = terraform.TerraformConfig(self._repo_base)
        except LookupError:
            self.terraform = None

    @staticmethod
    def config_file():
        """
        Name of the configuration file
        """
        return ".repoconfig"

    def secret_files(self):
        """
        List of sensitive files
        """
        result = "vault.txt,access_key.pem,aws_credentials,secrets.tfvars"

        if self._repository is not None:
            result = self._repository.get("secret_files", result)

        return filter(None, result.split(','))

# vim: ft=python:ts=4:sw=4