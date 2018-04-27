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
from autolibs.packer import PackerRepo


class PackerConfigMock:

    def __init__(self, packer_dir="/", config_file_path="envs_dir", packer_file_path="packer.json"):
        self.packer_dir = packer_dir
        self.config_file_path = config_file_path
        self.packer_file_path = packer_file_path

    def base_dir(self, full_path=False):
        return self.packer_dir

    def config_file(self):
        return self.config_file_path

    def packer_file(self):
        return self.packer_file_path


class PackerRepoTest(unittest.TestCase):

    def buildPackerRepo(self, repo_root=None, mck_pak_config=None, mck_is_git_repo=None, mck_repo_root=None, mck_is_pakbase_a_dir=None):
        """
        Builds a PackerRepo instance mocking all its constructor checks with working or given values
        """
        # Mock to check if the GIT repo root is valid
        is_git_repo_patch = patch('autolibs.utils.gitutils.is_git_repo')
        is_git_repo = is_git_repo_patch.start()
        is_git_repo.return_value = True if mck_is_git_repo is None else mck_is_git_repo

        # Mock for object PackerConfig
        pakconfig_patch = patch('autolibs.packer.config.PackerConfig')
        pakconfig = pakconfig_patch.start()
        pakconfig.return_value = PackerConfigMock() if mck_pak_config is None else mck_pak_config

        # Mock to get the GIT repo root
        get_git_root_patch = patch('autolibs.utils.gitutils.get_git_root')
        get_git_root = get_git_root_patch.start()
        get_git_root.return_value = "/repo_path" if mck_repo_root is None else mck_repo_root

        isdir_patch = patch('os.path.isdir')
        isdir = isdir_patch.start()
        isdir.return_value = True if mck_is_pakbase_a_dir is None else mck_is_pakbase_a_dir

        pakrepo = PackerRepo(repo_root)

        # Stop all patching
        isdir_patch.stop()
        pakconfig_patch.stop()
        is_git_repo_patch.stop()
        get_git_root_patch.stop()

        return pakrepo

    """ Creation """

    def test_reponotgiven_on_goodrepo(self):
        result = self.buildPackerRepo(mck_repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_reponotgiven_on_badrepo(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo(mck_repo_root="/repo_path", mck_is_git_repo=False)

    def test_goodrepo_given(self):
        result = self.buildPackerRepo(repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_badrepo_given(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo(repo_root="/repo_path", mck_is_git_repo=False)

    """ base """

    def test_base_notexisting_path(self):
        with self.assertRaises(IOError):
            result = self.buildPackerRepo(mck_is_pakbase_a_dir=False)

    def test_base_existing_path(self):
        result = self.buildPackerRepo(
            mck_pak_config=PackerConfigMock(packer_dir="pak_base")
        ).base
        self.assertEquals(result, "/repo_path/pak_base")
        self.assertTrue(os.path.isabs(result))

    """ images() """

    @patch('os.walk', return_value=[("", [])])
    def test_images_empty(self, *args):
        result = self.buildPackerRepo().images()
        self.assertListEqual(result, [])

    @patch('os.walk', return_value=[("", ["a", "b", "c"])])
    def test_images_valid(self, *args):
        result = self.buildPackerRepo().images()
        self.assertListEqual(result, ["a", "b", "c"])

    """ image_base(image) """

    def test_imagebase_image_none(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo().image_base(None)

    def test_imagebase_image_missing(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo().image_base("")

    def test_imagebase_image_notexisting(self):
        with self.assertRaises(IOError):
            result = self.buildPackerRepo().image_base("bad_image")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    def test_imagebase_image_notadir(self, *args):
        with self.assertRaises(IOError):
            result = self.buildPackerRepo().image_base("image_is_a_file")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_imagebase_image_correct(self, *args):
        result = self.buildPackerRepo().image_base("good_image")
        self.assertEquals(result, "/good_image")
        self.assertTrue(os.path.isabs(result))

    """ packer_file(image) """

    def test_pakfile_image_none(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo().packer_file(None)

    def test_pakfile_image_missing(self):
        with self.assertRaises(ValueError):
            result = self.buildPackerRepo().packer_file("")

    def test_pakfile_image_notexisting(self):
        with self.assertRaises(IOError):
            result = self.buildPackerRepo().packer_file("bad_image")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    def test_pakfile_image_notadir(self, *args):
        with self.assertRaises(IOError):
            result = self.buildPackerRepo().packer_file("image_is_a_file")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_pakfile_image_correct(self, *args):
        result = self.buildPackerRepo().packer_file("good_image")
        self.assertEquals(result, "/good_image/packer.json")
        self.assertTrue(os.path.isabs(result))

# vim: ft=python:ts=4:sw=4