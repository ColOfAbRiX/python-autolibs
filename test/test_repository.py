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
#

from __future__ import print_function

import unittest
from mock import patch

import autolibs
from autolibs.repository import RepoInfo


class RepoInfoTest(unittest.TestCase):

    def setUp(self):
        self.get_git_root_patch = patch('cfutils.gitutils.get_git_root')
        self.get_git_root = self.get_git_root_patch.start()

        self.is_git_repo_patch = patch('cfutils.gitutils.is_git_repo')
        self.is_git_repo = self.is_git_repo_patch.start()

    def tearDown(self):
        self.is_git_repo_patch.stop()
        self.get_git_root_patch.stop()

    """ Creation """

    def test_reponotgiven_on_goodrepo(self):
        self.get_git_root.return_value = "/good_repo-path"
        self.is_git_repo.return_value = True
        result = RepoInfo()
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/good_repo-path")

    def test_reponotgiven_on_badrepo(self):
        self.get_git_root.return_value = "/bad-path"
        self.is_git_repo.return_value = False
        with self.assertRaises(ValueError):
            result = RepoInfo()

    def test_goodrepo_given(self):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/good_repo-path")
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/good_repo-path")

    def test_badrepo_given(self):
        self.is_git_repo.return_value = False
        with self.assertRaises(ValueError):
            result = RepoInfo(repo_base="/bad-path")

    """ Members """

    @patch.object(autolibs.ansible.AnsibleRepo, '__init__', return_value=None)
    def test_ansible_present(self, ansible_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_with_ansible")
        self.assertIsNotNone(result.ansible)

    @patch.object(autolibs.ansible.AnsibleRepo, '__init__', side_effect=IOError())
    def test_ansible_present(self, ansible_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_without_ansible")
        self.assertIsNone(result.ansible)

    @patch.object(autolibs.terraform.TerraformRepo, '__init__', return_value=None)
    def test_terraform_present(self, terraform_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_with_terraform")
        self.assertIsNotNone(result.terraform)

    @patch.object(autolibs.terraform.TerraformRepo, '__init__', side_effect=IOError())
    def test_terraform_absent(self, terraform_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_without_terraform")
        self.assertIsNone(result.terraform)

    @patch.object(autolibs.packer.PackerRepo, '__init__', return_value=None)
    def test_packer_present(self, packer_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_with_packer")
        self.assertIsNotNone(result.packer)

    @patch.object(autolibs.packer.PackerRepo, '__init__', side_effect=IOError())
    def test_packer_absent(self, packer_mock):
        self.is_git_repo.return_value = True
        result = RepoInfo(repo_base="/path_without_packer")
        self.assertIsNone(result.packer)

# vim: ft=python:ts=4:sw=4