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
from mock import patch, mock_open

import os
from autolibs.ansible import AnsibleRepo


class AnsibleConstsMock:

    def __init__(self, values={'defaults': {}}):
        self.values = values

    def get_config(self, _p, section, name, env_var, default):
        return self.values[section].get(name, default)


class AnsibleConfigMock:

    def __init__(self, **kwargs):
        self.ansible_dir = kwargs.get("ansible_dir", "/")
        self.roles_dir_cfg = kwargs.get("roles_dir_cfg", "roles")
        self.playbooks_dir_cfg = kwargs.get("playbooks_dir_cfg", "playbooks")
        self.inventories_dir_cfg = kwargs.get("inventories_dir_cfg", "inventories")
        self.run_as_cfg = kwargs.get("run_as_cfg", None)
        self.dynainv_file_cfg = kwargs.get("dynainv_file_cfg", "inventory")
        self.vault_file_cfg = kwargs.get("vault_file_cfg", "vault.txt")
        self.ssh_key_file_cfg = kwargs.get("ssh_key_file_cfg", "access_key.pem")
        self.exec_ansible_cfg = kwargs.get("exec_ansible_cfg", "ansible")
        self.exec_ansible_playbook_cfg = kwargs.get("exec_ansible_playbook_cfg", "ansible-playbook")
        self.exec_ansible_vault_cfg = kwargs.get("exec_ansible_vault_cfg", "ansible-vault")

    def base_dir(self, full_path=False):
        return self.ansible_dir

    def roles_dir(self, full_path=False):
        return self.roles_dir_cfg

    def playbooks_dir(self, full_path=False):
        return self.playbooks_dir_cfg

    def inventories_dir(self, full_path=False):
        return self.inventories_dir_cfg

    def run_as(self):
        return self.run_as_cfg

    def dynamic_inventory_file(self):
        return self.dynainv_file_cfg

    def vault_file(self):
        return self.vault_file_cfg

    def ssh_key_file(self):
        return self.ssh_key_file_cfg

    def exec_ansible(self):
        return self.exec_ansible_cfg

    def exec_ansible_playbook(self):
        return self.exec_ansible_playbook_cfg

    def exec_ansible_vault(self):
        return self.exec_ansible_vault_cfg


def get_bin_path_mock(arg, opt_dirs=[]):
    return os.path.join("/usr/bin", arg)


class AnsibleRepoTest(unittest.TestCase):

    def buildAnsibleRepo(self, repo_root=None, mck_ans_config=None, mck_ans_consts=AnsibleConstsMock(), mck_is_git_repo=None, mck_repo_root=None, mck_is_ansbase_a_dir=None):
        """
        Builds a AnsibleRepo instance mocking all its constructor checks with working or given values
        """
        # Mock to check if the GIT repo root is valid
        is_git_repo_patch = patch('autolibs.utils.gitutils.is_git_repo')
        is_git_repo = is_git_repo_patch.start()
        is_git_repo.return_value = True if mck_is_git_repo is None else mck_is_git_repo

        # Mock for object AnsibleConfig
        ansibleconfig_patch = patch('autolibs.ansible.config.AnsibleConfig')
        ansibleconfig = ansibleconfig_patch.start()
        ansibleconfig.return_value = AnsibleConfigMock() if mck_ans_config is None else mck_ans_config

        # Mock to get the GIT repo root
        get_git_root_patch = patch('autolibs.utils.gitutils.get_git_root')
        get_git_root = get_git_root_patch.start()
        get_git_root.return_value = "/repo_path" if mck_repo_root is None else mck_repo_root

        # Mock the check that the base repo is a dir
        isdir_patch = patch('os.path.isdir')
        isdir = isdir_patch.start()
        isdir.return_value = True if mck_is_ansbase_a_dir is None else mck_is_ansbase_a_dir

        # Mock the object used to get the Ansible constants
        if mck_ans_consts is not None:
            chdir_patch = patch('os.chdir')
            chdir = chdir_patch.start()
            chdir.return_value = True

            load_config_file_patch = patch('autolibs.ansible.repository.C.load_config_file', return_value=(None, None))
            load_config_file = load_config_file_patch.start()

            get_config_patch = patch('autolibs.ansible.repository.C.get_config')
            get_config = get_config_patch.start()
            get_config.side_effect = mck_ans_consts.get_config

        ansiblerepo = AnsibleRepo(repo_root)

        # Stop all patching
        isdir_patch.stop()
        ansibleconfig_patch.stop()
        is_git_repo_patch.stop()
        get_git_root_patch.stop()

        if mck_ans_consts is not None:
            chdir_patch.stop()
            load_config_file_patch.stop()
            get_config_patch.stop()

        return ansiblerepo

    """ Creation """

    def test_reponotgiven_on_goodrepo(self):
        result = self.buildAnsibleRepo(mck_repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_reponotgiven_on_badrepo(self):
        with self.assertRaises(ValueError):
            result = self.buildAnsibleRepo(mck_repo_root="/repo_path", mck_is_git_repo=False)

    def test_goodrepo_given(self):
        result = self.buildAnsibleRepo(repo_root="/repo_path", mck_is_git_repo=True)
        self.assertIsNotNone(result)
        self.assertEquals(result.repo_base, "/repo_path")

    def test_badrepo_given(self):
        with self.assertRaises(ValueError):
            result = self.buildAnsibleRepo(repo_root="/repo_path", mck_is_git_repo=False)

    """ base """

    def test_base_notexisting_path(self):
        with self.assertRaises(IOError):
            result = self.buildAnsibleRepo(mck_is_ansbase_a_dir=False)

    def test_base_existing_path(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(ansible_dir="ansible_base")
        ).base
        self.assertEquals(result, "/repo_path/ansible_base")
        self.assertTrue(os.path.isabs(result))

    """ roles_base """

    def test_roles_base(self):
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                roles_dir_cfg="test_roles"
            )
        ).roles_base
        self.assertEquals(result, "/repo_path/ansible_base/test_roles")
        self.assertTrue(os.path.isabs(result))

    """ playbooks_base """

    def test_playbooks_base(self):
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                playbooks_dir_cfg="test_playbooks"
            )
        ).playbooks_base
        self.assertEquals(result, "/repo_path/ansible_base/test_playbooks")
        self.assertTrue(os.path.isabs(result))

    """ inventory_base """

    def test_inventory_base(self):
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            ),
            mck_ans_consts=AnsibleConstsMock(
                values={'defaults': {'inventory': 'test_inventory'}}
            )
        ).inventory_base
        self.assertEquals(result, "/repo_path/ansible_base/test_inventory")
        self.assertTrue(os.path.isabs(result))

    """ run_as """

    def test_run_as(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                run_as_cfg="test_user"
            )
        ).run_as
        self.assertEquals(result, "test_user")

    """ vault_file """

    def test_vault_file(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                vault_file_cfg="test_vault_file"
            )
        ).vault_file
        self.assertEquals(result, "test_vault_file")
        self.assertTrue(result.find('/') == -1)

    """ ssh_key """

    def test_ssh_key(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                ssh_key_file_cfg="test_ssh_key"
            )
        ).ssh_key
        self.assertEquals(result, "test_ssh_key")
        self.assertTrue(result.find('/') == -1)

    """ dynainv_file """

    def test_dynainv_file(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                dynainv_file_cfg="test_dynainv_file"
            )
        ).dynainv_file
        self.assertEquals(result, "test_dynainv_file")
        self.assertTrue(result.find('/') == -1)

    """ dynainv_path """

    def test_dynainv_path(self):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                dynainv_path_cfg="test_dynainv_path"
            )
        ).dynainv_path
        self.assertEquals(result, "/repo_path/ansible_base/scripts/inventory")
        self.assertTrue(os.path.isabs(result))

    """ ansible """

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_from_config(self, *args):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                exec_ansible_cfg="ansible_cmd"
            )
        ).ansible
        self.assertEquals(result, "/usr/bin/ansible_cmd")

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_from_env(self, *args):
        os.environ['ANSIBLE'] = "ansible_cmd"
        result = self.buildAnsibleRepo().ansible
        self.assertEquals(result, "/usr/bin/ansible_cmd")

    """ ansible_playbook """

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_playbook_from_config(self, *args):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                exec_ansible_playbook_cfg="ansible_playbook_cmd"
            )
        ).ansible_playbook
        self.assertEquals(result, "/usr/bin/ansible_playbook_cmd")

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_playbook_from_env(self, *args):
        os.environ['ANSIBLE_PLAYBOOK'] = "ansible_playbook_cmd"
        result = self.buildAnsibleRepo().ansible_playbook
        self.assertEquals(result, "/usr/bin/ansible_playbook_cmd")

    """ ansible_vault """

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_vault_from_config(self, *args):
        result = self.buildAnsibleRepo(
            mck_ans_config=AnsibleConfigMock(
                exec_ansible_vault_cfg="ansible_vault_cmd"
            )
        ).ansible_vault
        self.assertEquals(result, "/usr/bin/ansible_vault_cmd")

    @patch('autolibs.ansible.repository.get_bin_path', side_effect=get_bin_path_mock)
    def test_ansible_vault_from_env(self, *args):
        os.environ['ANSIBLE_VAULT'] = "ansible_vault_cmd"
        result = self.buildAnsibleRepo().ansible_vault
        self.assertEquals(result, "/usr/bin/ansible_vault_cmd")

    """ ans_config(self, section, name, default) """

    @patch('autolibs.ansible.repository.C.get_config')
    def test_get_config_value(self, mock):
        mock.side_effect = AnsibleConstsMock(
            values={'defaults': {'test_key': 'test_value'}}
        ).get_config
        result = self.buildAnsibleRepo().ans_config(
            'defaults', 'test_key', 'default_value'
        )
        self.assertEquals(result, "test_value")

    @patch('autolibs.ansible.repository.C.get_config')
    def test_get_config_default(self, mock):
        mock.side_effect = AnsibleConstsMock(
            values={'defaults': {'test_key': 'test_value'}}
        ).get_config
        result = self.buildAnsibleRepo().ans_config(
            'defaults', 'missing_test_key', 'default_value'
        )
        self.assertEquals(result, "default_value")

    """ playbooks(self) """

    @patch('os.walk')
    def test_playbooks_empty_dir(self, mock):
        mock.return_value = []
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                playbooks_dir_cfg="test_playbooks"
            )
        ).playbooks()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    def test_playbooks_skip_git(self, mock):
        mock.return_value = [
            ('/repo_path/ansible_base/test_playbooks/.git', [], ['playbook_1.yml', 'playbook_2.yml', 'playbook_3.yml'])
        ]
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                playbooks_dir_cfg="test_playbooks"
            )
        ).playbooks()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    def test_playbooks_plain(self, mock):
        mock.return_value = [
            ('/repo_path/ansible_base/test_playbooks/', [], ['playbook_1.yml', 'playbook_2.yml', 'playbook_3.yml'])
        ]
        expected = [
            '/repo_path/ansible_base/test_playbooks/playbook_1.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_2.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_3.yml'
        ]
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                playbooks_dir_cfg="test_playbooks"
            )
        ).playbooks()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    def test_playbooks_subdirs(self, mock):
        mock.return_value = [
            ('/repo_path/ansible_base/test_playbooks/subdir_1', [], ['playbook_1.yml', 'playbook_2.yml', 'playbook_3.yml']),
            ('/repo_path/ansible_base/test_playbooks/subdir_2', [], ['playbook_1.yml', 'playbook_2.yml']),
            ('/repo_path/ansible_base/test_playbooks/', ['subdir_1', 'subdir_2'], ['playbook_1.yml', 'playbook_2.yml', 'playbook_3.yml', 'playbook_4.yml'])
        ]
        expected = [
            '/repo_path/ansible_base/test_playbooks/subdir_1/playbook_1.yml',
            '/repo_path/ansible_base/test_playbooks/subdir_1/playbook_2.yml',
            '/repo_path/ansible_base/test_playbooks/subdir_1/playbook_3.yml',
            '/repo_path/ansible_base/test_playbooks/subdir_2/playbook_1.yml',
            '/repo_path/ansible_base/test_playbooks/subdir_2/playbook_2.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_1.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_2.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_3.yml',
            '/repo_path/ansible_base/test_playbooks/playbook_4.yml'
        ]
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base",
                playbooks_dir_cfg="test_playbooks"
            )
        ).playbooks()
        self.assertListEqual(result, expected)

    """ vaulted(self) """

    @patch('os.walk')
    def test_vaulted_empty_dir(self, mock):
        mock.return_value = []
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).vaulted()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    @patch('__builtin__.open')
    def test_vaulted_no_vaults(self, mock_open, mock_walk):
        mock_open.return_value = string_io('Content 1', 'Content 21\nContent 22', 'Content 3')
        mock_walk.return_value = [
            ('/repo_path/ansible_base', [], ['file_1.yml', 'file_2.yml', 'file_3.yml'])
        ]
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).vaulted()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    @patch('__builtin__.open')
    def test_vaulted_cannot_open(self, mock_open, mock_walk):
        mock_walk.return_value = []
        mock_open.side_effect = IOError()
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).vaulted()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    def test_vaulted_skip_git(self, mock):
        mock.return_value = [
            ('/repo_path/ansible_base/.git', [], ['file_1.yml', 'file_2.yml', 'file_3.yml'])
        ]
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).vaulted()
        self.assertListEqual(result, expected)

    @patch('os.walk')
    @patch('__builtin__.open')
    def test_vaulted_vaulted(self, mock_open, mock_walk):
        mock_open.return_value = string_io('$ANSIBLE_VAULT;1.1;AES256', 'Content 2', '$ANSIBLE_VAULT;1.1;AES256')
        mock_walk.return_value = [
            ('/repo_path/ansible_base', [], ['file_1.yml', 'file_2.yml', 'file_3.yml'])
        ]
        expected = [
            '/repo_path/ansible_base/file_1.yml',
            '/repo_path/ansible_base/file_3.yml'
        ]
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).vaulted()
        self.assertListEqual(result, expected)

    """ tags(self) """

    @patch('glob.glob')
    def test_tags_empty_dir(self, mock_glob):
        mock_glob.return_value = []
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).tags()
        self.assertListEqual(result, expected)

    @patch('glob.glob')
    @patch('__builtin__.open')
    def test_tags_cannot_open(self, mock_open, mock_glob):
        mock_glob.return_value = []
        mock_open.side_effect = IOError()
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).tags()
        self.assertListEqual(result, expected)

    @patch('glob.glob')
    @patch('__builtin__.open')
    def test_tags_badyaml_content(self, mock_open, mock_glob):
        mock_open.return_value = string_io('not_a_yaml_content')
        mock_glob.return_value = ['file_1.yml']
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).tags()
        self.assertListEqual(result, expected)

    @patch('glob.glob')
    @patch('__builtin__.open')
    def test_tags_notags(self, mock_open, mock_glob):
        mock_open.return_value = string_io('- {name: missing tags}')
        mock_glob.return_value = ['file_1.yml']
        expected = []
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).tags()
        self.assertListEqual(result, expected)

    @patch('glob.glob')
    @patch('__builtin__.open')
    def test_tags_tags(self, mock_open, mock_glob):
        mock_open.return_value = string_io(
            '[{tags: [tag_1, tag_2]}, {name: no tags here}, {tags: tags_3}]'
        )
        mock_glob.return_value = ['file_1.yml']
        expected = ['tag_1', 'tag_2', 'tags_3']
        result = self.buildAnsibleRepo(
            repo_root="/repo_path",
            mck_ans_config=AnsibleConfigMock(
                ansible_dir="ansible_base"
            )
        ).tags()
        self.assertListEqual(result, expected)


def string_io(*texts):
    """
    Using a StringIO so I can mock open. Found this trick here:
    https://stackoverflow.com/questions/12028637/pythons-stringio-doesnt-do-well-with-with-statements
    """
    from StringIO import StringIO
    StringIO.__exit__ = lambda *args: args[0]
    StringIO.__enter__ = lambda *args: args[0]
    return StringIO(unicode('\n'.join(texts), 'utf-8'))

# vim: ft=python:ts=4:sw=4