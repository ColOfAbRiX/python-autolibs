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
from autolibs.terraform import TerraformRepo
from autolibs.utils.common import get_builtins_ref


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

    def buildTFRepo(self, repo_root=None, mck_tf_config=None, mck_is_git_repo=None, mck_repo_root=None, mck_is_tfbase_a_dir=None):
        """
        Builds a TerraformRepo instance mocking all its constructor checks with working or given values
        """
        # Mock to check if the GIT repo root is valid
        is_git_repo_patch = patch('autolibs.utils.gitutils.is_git_repo')
        is_git_repo = is_git_repo_patch.start()
        is_git_repo.return_value = True if mck_is_git_repo is None else mck_is_git_repo

        # Mock for object TerraformConfig
        tfconfig_patch = patch('autolibs.terraform.config.TerraformConfig')
        tfconfig = tfconfig_patch.start()
        tfconfig.return_value = TerraformConfigMock() if mck_tf_config is None else mck_tf_config

        # Mock to get the GIT repo root
        get_git_root_patch = patch('autolibs.utils.gitutils.get_git_root')
        get_git_root = get_git_root_patch.start()
        get_git_root.return_value = "/repo_path" if mck_repo_root is None else mck_repo_root

        isdir_patch = patch('os.path.isdir')
        isdir = isdir_patch.start()
        isdir.return_value = True if mck_is_tfbase_a_dir is None else mck_is_tfbase_a_dir

        tfrepo = TerraformRepo(repo_root)

        # Stop all patching
        isdir_patch.stop()
        tfconfig_patch.stop()
        is_git_repo_patch.stop()
        get_git_root_patch.stop()

        return tfrepo

    """ Creation """

    def test_reponotgiven_on_goodrepo(self):
        result = self.buildTFRepo(mck_repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_reponotgiven_on_badrepo(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo(mck_repo_root="/repo_path", mck_is_git_repo=False)

    def test_goodrepo_given(self):
        result = self.buildTFRepo(repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_badrepo_given(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo(repo_root="/repo_path", mck_is_git_repo=False)

    """ base """

    def test_base_notexisting_path(self):
        with self.assertRaises(IOError):
            result = self.buildTFRepo(mck_is_tfbase_a_dir=False)

    def test_base_existing_path(self):
        result = self.buildTFRepo(
            mck_tf_config=TerraformConfigMock(tf_dir="tf_base")
        ).base
        self.assertEquals(result, "/repo_path/tf_base")
        self.assertTrue(os.path.isabs(result))

    """ environments_base """

    def test_envsbase_correct_path(self):
        result = self.buildTFRepo(
            mck_tf_config=TerraformConfigMock(tf_dir="tf_base", envs_dir="envs_dir")
        ).environments_base
        self.assertEquals(result, "/repo_path/tf_base/envs_dir")
        self.assertTrue(os.path.isabs(result))

    """ environments() """

    @patch(get_builtins_ref() + '.next', return_value=[[], ["dir_1", "dir_2"]])
    def test_list_environments(self, *args):
        result = self.buildTFRepo().environments()
        self.assertListEqual(result, ["dir_1", "dir_2"])

    @patch(get_builtins_ref() + '.next', return_value=[[], []])
    def test_list_empty_envs(self, *args):
        result = self.buildTFRepo().environments()
        self.assertListEqual(result, [])

    """ environment_base() """

    def test_envbase_env_none(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo().environment_base(None)

    def test_envbase_env_missing(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo().environment_base("")

    def test_envbase_env_notexisting(self):
        with self.assertRaises(IOError):
            result = self.buildTFRepo().environment_base("bad_environment")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    def test_envbase_env_notadir(self, *args):
        with self.assertRaises(IOError):
            result = self.buildTFRepo().environment_base("env_is_a_file")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_envbase_env_correct(self, *args):
        result = self.buildTFRepo().environment_base("good_environment")
        self.assertEquals(result, "/envs_dir/good_environment")
        self.assertTrue(os.path.isabs(result))

    """ state_file """

    def test_stfile_env_none(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo().state_file(None)

    def test_stfile_env_missing(self):
        with self.assertRaises(ValueError):
            result = self.buildTFRepo().state_file("")

    def test_stfile_env_notexisting(self):
        with self.assertRaises(IOError):
            result = self.buildTFRepo().state_file("bad_env")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    def test_stfile_env_notadir(self, *args):
        with self.assertRaises(IOError):
            result = self.buildTFRepo().state_file("env_is_a_file")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_stfile_env_correct(self, *args):
        result = self.buildTFRepo().state_file("good_environment")
        self.assertEquals(result, "/envs_dir/good_environment/terraform.tfstate")
        self.assertTrue(os.path.isabs(result))

# vim: ft=python:ts=4:sw=4