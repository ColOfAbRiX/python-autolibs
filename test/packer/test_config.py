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
import autolibs
from autolibs.packer.config import PackerConfig


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
        self.config_parser_patch = patch('configparser.ConfigParser', autospec=True)
        self.config_parser = self.config_parser_patch.start()

    def tearDown(self):
        self.config_parser_patch.stop()

    """ Creation """

    def test_missing_repo_root(self):
        with self.assertRaises(ValueError):
            result = PackerConfig("bad_path")

    """ config_file """

    def test_config_file(self):
        result = PackerConfig("/").config_file
        self.assertEquals(result, "/.repoconfig")

    """ config """

    def test_missing_file(self):
        result = PackerConfig("/").config
        self.assertIsNone(result)

    def test_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = PackerConfig("/").config
        self.assertIsNone(result)

    def test_PackerConfig(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['packer'],
            content={'packer': {}}
        )
        result = PackerConfig("/").config
        self.assertIsNotNone(result)

    """ base_dir() """

    def test_base_dir_default_on_missing_file(self):
        result = PackerConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = PackerConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['packer'],
            content={'packer': {}}
        )
        result = PackerConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['packer'],
            content={'packer': {'base_dir': 'test_dir'}}
        )
        result = PackerConfig("/").base_dir()
        self.assertEquals(result, 'test_dir')

    def test_base_dir_value_abspath(self):
        self.config_parser.return_value = ConfigParserMock()
        result = PackerConfig("/").base_dir(full_path=True)
        self.assertTrue(os.path.isabs(result))

    """ packer_file() """

    def test_packer_file_default_on_missing_file(self):
        result = PackerConfig("/").packer_file()
        self.assertTrue(len(result) > 0)

    def test_packer_file_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = PackerConfig("/").packer_file()
        self.assertTrue(len(result) > 0)

    def test_packer_file_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['packer'],
            content={'packer': {}}
        )
        result = PackerConfig("/").packer_file()
        self.assertTrue(len(result) > 0)

    def test_packer_file_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['packer'],
            content={'packer': {'packer_file': 'test_file'}}
        )
        result = PackerConfig("/").packer_file()
        self.assertEquals(result, 'test_file')

# vim: ft=python:ts=4:sw=4