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

import os
from autolibs import TerraformRepo


class TerraformConfigMock:

    def __init__(self, tf_dir="/", envs_dir="envs_dir", tfstate_file="terraform.tfstate"):
        self.tf_dir = tf_dir
        self.envs_dir = envs_dir
        self.tfstate_file = tfstate_file

    def base_dir(self, full_path=False):
        return self.tf_dir

    def environments_dir(self, full_path=False):
        return self.envs_dir

    def state_file(self):
        return self.tfstate_file


class TerraformRepoTest(unittest.TestCase):

    def setUp(self):
        # Mock to get the GIT repo root
        self.get_git_root_patch = patch('cfutils.gitutils.get_git_root')
        self.get_git_root = self.get_git_root_patch.start()

        # Mock to check if the GIT repo root is valid
        self.is_git_repo_patch = patch('cfutils.gitutils.is_git_repo')
        self.is_git_repo = self.is_git_repo_patch.start()
        self.is_git_repo.return_value = True

        # Mock for object TerraformConfig
        self.tfconfig_patch = patch('autolibs.terraform.config.TerraformConfig')
        self.tfconfig = self.tfconfig_patch.start()
        self.tfconfig.return_value = TerraformConfigMock()

    def tearDown(self):
        self.tfconfig_patch.stop()
        self.is_git_repo_patch.stop()
        self.get_git_root_patch.stop()

    """ Creation """

    def test_reponotgiven_on_goodrepo(self):
        self.get_git_root.return_value = "/good_repo-path"
        result = TerraformRepo()
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/good_repo-path")

    def test_reponotgiven_on_badrepo(self):
        self.get_git_root.return_value = "/bad-path"
        self.is_git_repo.return_value = False
        with self.assertRaises(ValueError):
            result = TerraformRepo()

    def test_goodrepo_given(self):
        result = TerraformRepo(repo_base="/good_repo-path")
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/good_repo-path")

    def test_badrepo_given(self):
        self.is_git_repo.return_value = False
        with self.assertRaises(ValueError):
            result = TerraformRepo(repo_base="/bad-path")

    def test_bad_base_path(self):
        self.tfconfig.return_value = TerraformConfigMock(tf_dir="doesnt_exist")
        with self.assertRaises(IOError):
            result = TerraformRepo(repo_base="/non_existent-path")

    """ base """

    def test_base_notexisting_path(self):
        self.tfconfig.return_value = TerraformConfigMock(tf_dir="tf_base")
        with self.assertRaises(IOError):
            result = TerraformRepo(repo_base="/non_existent-path").base

    @patch('os.path.isdir', return_value=True)
    def test_base_existing_path(self, *args):
        self.tfconfig.return_value = TerraformConfigMock(tf_dir="tf_base")
        result = TerraformRepo(repo_base="/good_repo-path").base
        self.assertEquals(result, "/good_repo-path/tf_base")

    def test_base_is_abspath(self, *args):
        pass

    """ environments_base """

    @patch('os.path.isdir', return_value=True)
    def test_envsbase_correct_path(self, *args):
        self.tfconfig.return_value = TerraformConfigMock(tf_dir="tf_base")
        result = TerraformRepo(repo_base="/good_repo-path").base
        self.assertEquals(result, "/good_repo-path/tf_base")

    def test_envsbase_is_abspath(self, *args):
        pass

    """ environments() """

    @patch('__builtin__.next', return_value=[[], ["dir_1", "dir_2"]])
    def test_list_environments(self, *args):
        result = TerraformRepo().environments()
        self.assertListEqual(result, ["dir_1", "dir_2"])

    @patch('__builtin__.next', return_value=[[], []])
    def test_list_empty_envs(self, *args):
        result = TerraformRepo().environments()
        self.assertListEqual(result, [])

    """ environment_base() """

    def test_envbase_env_none(self):
        with self.assertRaises(ValueError):
            result = TerraformRepo().environment_base(None)

    def test_envbase_env_missing(self):
        with self.assertRaises(ValueError):
            result = TerraformRepo().environment_base("")

    def test_envbase_env_notexisting(self):
        with self.assertRaises(IOError):
            result = TerraformRepo().environment_base("bad_env")

    def test_envbase_env_notadir(self):
        pass

    def test_envbase_env_correct(self):
        pass

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_envbase_is_abspath(self, *args):
        result = TerraformRepo().environment_base("env-1")
        self.assertTrue(os.path.isabs(result))

    """ state_file """

    def test_stfile_env_none(self):
        with self.assertRaises(ValueError):
            result = TerraformRepo().state_file(None)

    def test_stfile_env_missing(self):
        with self.assertRaises(ValueError):
            result = TerraformRepo().state_file("")

    def test_stfile_env_notexisting(self):
        with self.assertRaises(IOError):
            result = TerraformRepo().state_file("bad_env")

    def test_stfile_env_notadir(self):
        pass

    def test_stfile_env_correct(self):
        pass

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_stfile_is_abspath(self, *args):
        result = TerraformRepo().state_file("env-1")
        self.assertTrue(os.path.isabs(result))

# vim: ft=python:ts=4:sw=4