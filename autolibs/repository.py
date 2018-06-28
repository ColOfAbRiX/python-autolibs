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
import git
from git.exc import NoSuchPathError
from autolibs.utils import gitutils
from autolibs import config, packer, ansible, terraform


class RepoInfo:
    """
    Information about an Automation Repository
    """
    def __init__(self, repo_base=None):
        # Get repository base
        if repo_base is None:
            repo_base = gitutils.get_git_root()

        if not gitutils.is_git_repo(repo_base):
            raise ValueError("Not a GIT repository: %s" % repo_base)

        self.repo_base = repo_base

        # Ansible
        try:
            self.ansible = ansible.AnsibleRepo(self.repo_base)
        except (LookupError, IOError, NoSuchPathError):
            self.ansible = None

        # Packer
        try:
            self.packer = packer.PackerRepo(self.repo_base)
        except (LookupError, IOError, NoSuchPathError):
            self.packer = None

        # Terraform
        try:
            self.terraform = terraform.TerraformRepo(self.repo_base)
        except (LookupError, IOError, NoSuchPathError):
            self.terraform = None

# vim: ft=python:ts=4:sw=4