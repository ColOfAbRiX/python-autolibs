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
from autolibs.ansible.config import AnsibleConfig


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

    @patch('os.path.isdir', return_value=False)
    def test_missing_repo_root(self, *args):
        with self.assertRaises(ValueError):
            result = AnsibleConfig("bad_path")

    """ config_file """

    def test_config_file(self):
        result = AnsibleConfig("/").config_file
        self.assertEquals(result, "/.repoconfig")

    """ config """

    def test_missing_file(self):
        result = AnsibleConfig("/").config
        self.assertIsNone(result)

    def test_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").config
        self.assertIsNone(result)

    def test_AnsibleConfig(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").config
        self.assertIsNotNone(result)

    """ base_dir() """

    def test_base_dir_default_on_missing_file(self):
        result = AnsibleConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").base_dir()
        self.assertTrue(len(result) > 0)

    def test_base_dir_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'base_dir': 'test_dir'}}
        )
        result = AnsibleConfig("/").base_dir()
        self.assertEquals(result, 'test_dir')

    def test_base_dir_value_abspath(self):
        self.config_parser.return_value = ConfigParserMock()
        result = AnsibleConfig("/").base_dir(full_path=True)
        self.assertTrue(os.path.isabs(result))

    """ roles_dir(self, full_path) """

    def test_roles_dir_default_on_missing_file(self):
        result = AnsibleConfig("/").roles_dir()
        self.assertTrue(len(result) > 0)

    def test_roles_dir_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").roles_dir()
        self.assertTrue(len(result) > 0)

    def test_roles_dir_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").roles_dir()
        self.assertTrue(len(result) > 0)

    def test_roles_dir_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'roles_dir': 'test_dir'}}
        )
        result = AnsibleConfig("/").roles_dir()
        self.assertEquals(result, 'test_dir')

    def test_roles_dir_value_abspath(self):
        self.config_parser.return_value = ConfigParserMock()
        result = AnsibleConfig("/").roles_dir(full_path=True)
        self.assertTrue(os.path.isabs(result))

    """ playbooks_dir(self, full_path) """

    def test_playbooks_dir_default_on_missing_file(self):
        result = AnsibleConfig("/").playbooks_dir()
        self.assertTrue(len(result) > 0)

    def test_playbooks_dir_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").playbooks_dir()
        self.assertTrue(len(result) > 0)

    def test_playbooks_dir_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").playbooks_dir()
        self.assertTrue(len(result) > 0)

    def test_playbooks_dir_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'playbooks_dir': 'test_dir'}}
        )
        result = AnsibleConfig("/").playbooks_dir()
        self.assertEquals(result, 'test_dir')

    def test_playbooks_dir_value_abspath(self):
        self.config_parser.return_value = ConfigParserMock()
        result = AnsibleConfig("/").playbooks_dir(full_path=True)
        self.assertTrue(os.path.isabs(result))

    """ inventories_dir(self, full_path) """

    def test_inventories_dir_default_on_missing_file(self):
        result = AnsibleConfig("/").inventories_dir()
        self.assertTrue(len(result) > 0)

    def test_inventories_dir_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").inventories_dir()
        self.assertTrue(len(result) > 0)

    def test_inventories_dir_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").inventories_dir()
        self.assertTrue(len(result) > 0)

    def test_inventories_dir_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'inventories_dir': 'test_dir'}}
        )
        result = AnsibleConfig("/").inventories_dir()
        self.assertEquals(result, 'test_dir')

    def test_inventories_dir_value_abspath(self):
        self.config_parser.return_value = ConfigParserMock()
        result = AnsibleConfig("/").inventories_dir(full_path=True)
        self.assertTrue(os.path.isabs(result))

    """ run_as(self) """

    def test_run_as_default_on_missing_file(self):
        result = AnsibleConfig("/").run_as()
        self.assertIsNone(result)

    def test_run_as_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").run_as()
        self.assertIsNone(result)

    def test_run_as_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").run_as()
        self.assertIsNone(result)

    def test_run_as_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'run_as': 'test_dir'}}
        )
        result = AnsibleConfig("/").run_as()
        self.assertEquals(result, 'test_dir')

    """ dynamic_inventory_file(self) """

    def test_dynamic_inventory_file_default_on_missing_file(self):
        result = AnsibleConfig("/").dynamic_inventory_file()
        self.assertTrue(len(result) > 0)

    def test_dynamic_inventory_file_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").dynamic_inventory_file()
        self.assertTrue(len(result) > 0)

    def test_dynamic_inventory_file_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").dynamic_inventory_file()
        self.assertTrue(len(result) > 0)

    def test_dynamic_inventory_file_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'dynamic_inventory_file': 'test_dir'}}
        )
        result = AnsibleConfig("/").dynamic_inventory_file()
        self.assertEquals(result, 'test_dir')

    """ vault_file(self) """

    def test_vault_file_default_on_missing_file(self):
        result = AnsibleConfig("/").vault_file()
        self.assertTrue(len(result) > 0)

    def test_vault_file_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").vault_file()
        self.assertTrue(len(result) > 0)

    def test_vault_file_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").vault_file()
        self.assertTrue(len(result) > 0)

    def test_vault_file_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'vault_file': 'test_dir'}}
        )
        result = AnsibleConfig("/").vault_file()
        self.assertEquals(result, 'test_dir')

    """ ssh_key_file(self) """

    def test_ssh_key_file_default_on_missing_file(self):
        result = AnsibleConfig("/").ssh_key_file()
        self.assertTrue(len(result) > 0)

    def test_ssh_key_file_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").ssh_key_file()
        self.assertTrue(len(result) > 0)

    def test_ssh_key_file_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").ssh_key_file()
        self.assertTrue(len(result) > 0)

    def test_ssh_key_file_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'ssh_key_file': 'test_dir'}}
        )
        result = AnsibleConfig("/").ssh_key_file()
        self.assertEquals(result, 'test_dir')

    """ exec_ansible(self) """

    def test_exec_ansible_default_on_missing_file(self):
        result = AnsibleConfig("/").exec_ansible()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").exec_ansible()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").exec_ansible()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'exec_ansible': 'test_dir'}}
        )
        result = AnsibleConfig("/").exec_ansible()
        self.assertEquals(result, 'test_dir')

    """ exec_ansible_playbook(self) """

    def test_exec_ansible_playbook_default_on_missing_file(self):
        result = AnsibleConfig("/").exec_ansible_playbook()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_playbook_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").exec_ansible_playbook()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_playbook_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").exec_ansible_playbook()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_playbook_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'exec_ansible_playbook': 'test_dir'}}
        )
        result = AnsibleConfig("/").exec_ansible_playbook()
        self.assertEquals(result, 'test_dir')

    """ exec_ansible_vault(self) """

    def test_exec_ansible_vault_default_on_missing_file(self):
        result = AnsibleConfig("/").exec_ansible_vault()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_vault_default_on_missing_section(self):
        self.config_parser.return_value = ConfigParserMock(sections=[])
        result = AnsibleConfig("/").exec_ansible_vault()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_vault_default_on_missing_key(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {}}
        )
        result = AnsibleConfig("/").exec_ansible_vault()
        self.assertTrue(len(result) > 0)

    def test_exec_ansible_vault_value(self):
        self.config_parser.return_value = ConfigParserMock(
            sections=['ansible'],
            content={'ansible': {'exec_ansible_vault': 'test_dir'}}
        )
        result = AnsibleConfig("/").exec_ansible_vault()
        self.assertEquals(result, 'test_dir')
