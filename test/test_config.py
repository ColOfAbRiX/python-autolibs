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
from autolibs.config import Config


class ConfigParserMock:

    def __init__(self, sections=[], content={}):
        self.sects = sections
        self.content = content

    def sections(self):
        return self.sects

    def read(self, filename):
        pass

    def __getitem__(self, key):
        if key not in self.content.keys():
            raise KeyError
        return self.content[key]


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.ansible_patch = patch('autolibs.ansible.AnsibleConfig', autospec=True, return_value=None)
        self.ansible = self.ansible_patch.start()

        self.terraform_patch = patch('autolibs.terraform.TerraformConfig', autospec=True, return_value=None)
        self.terraform = self.terraform_patch.start()

        self.packer_patch = patch('autolibs.packer.PackerConfig', autospec=True, return_value=None)
        self.packer = self.packer_patch.start()

        self.config_parser_patch = patch('configparser.ConfigParser', autospec=True)
        self.config_parser = self.config_parser_patch.start()

    def tearDown(self):
        self.ansible_patch.stop()
        self.terraform_patch.stop()
        self.packer_patch.stop()
        self.config_parser_patch.stop()

    """ Creation """

    @patch('os.path.isdir', return_value=False)
    def test_missing_repo_root(self, *args):
        with self.assertRaises(ValueError):
            result = Config("bad_path")

    """ config_file """

    def test_config_file(self):
        result = Config("/").config_file
        self.assertEquals(result, "/.repoconfig")

    """ config """

    def test_missing_file(self):
        result = Config("/").config
        self.assertIsNone(result)

    def test_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = Config("/").config
        self.assertIsNone(result)

    def test_config(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['repository'],
            content={'repository': {}}
        )
        result = Config("/").config
        self.assertIsNotNone(result)

    """ ansible """

    def test_ansible_notpresent(self):
        self.ansible.side_effect = LookupError()
        result = Config(repo_base="/").ansible
        self.assertIsNone(result)

    def test_ansible_present(self):
        self.ansible.return_value = "DummyValue"
        result = Config(repo_base="/").ansible
        self.assertIsNotNone(result)

    """ terraform """

    def test_terraform_notpresent(self):
        self.terraform.side_effect = LookupError()
        result = Config(repo_base="/").terraform
        self.assertIsNone(result)

    def test_terraform_present(self):
        self.terraform.return_value = "DummyValue"
        result = Config(repo_base="/").terraform
        self.assertIsNotNone(result)

    """ packer """

    def test_packer_notpresent(self):
        self.packer.side_effect = LookupError()
        result = Config(repo_base="/").packer
        self.assertIsNone(result)

    def test_packer_present(self):
        self.packer.return_value = "DummyValue"
        result = Config(repo_base="/").packer
        self.assertIsNotNone(result)

    """ secret_files() """

    def test_secret_files_default_on_missing_file(self):
        result = Config("/").secret_files()
        self.assertTrue(len(result) > 0)

    def test_secret_files_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = Config("/").secret_files()
        self.assertTrue(len(result) > 0)

    def test_secret_files_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['repository'],
            content={'repository': {}}
        )
        result = Config("/").secret_files()
        self.assertTrue(len(result) > 0)

    def test_secret_files_empty_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['repository'],
            content={'repository': {'secret_files': ''}}
        )
        result = Config("/").secret_files()
        self.assertListEqual(result, [])

    def test_secret_files_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['repository'],
            content={'repository': {'secret_files': 'test_secret_1,test_secret_2'}}
        )
        result = Config("/").secret_files()
        self.assertListEqual(result, ['test_secret_1', 'test_secret_2'])

# vim: ft=python:ts=4:sw=4