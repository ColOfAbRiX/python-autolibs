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

import os
import configparser
from cfutils.gitutils import *


class AnsibleConfig:
    """
    Ansible Section Configuration
    """
    def __init__(self, repo_base):
        if not os.path.isdir(repo_base):
            raise ValueError("Not a valid path: %s" % repo_base)
        self._repo_base = repo_base

        self.config_file = os.path.join(self._repo_base, self.config_file())
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if "ansible" not in self.config.sections():
            self.config = None
            self._ansible = None
        else:
            self._ansible = self.config['ansible']

    @staticmethod
    def config_file():
        """
        Name of the configuration file
        """
        return ".repoconfig"

    def base_dir(self, full_path=False):
        """
        Base directory of Ansible
        """
        result = "ansible"

        if self._ansible is not None:
            result = self._ansible.get("base_dir", result)

        if full_path:
            result = os.path.join(self._repo_base, result)

        return result

    def roles_dir(self, full_path=False):
        """
        Directory containing the roles
        """
        result = "roles"

        if self._ansible is not None:
            result = self._ansible.get("roles_dir", result)

        if full_path:
            result = os.path.join(self.base_dir(True), result)

        return result

    def playbooks_dir(self, full_path=False):
        """
        Directory containing the playbooks
        """
        result = "playbooks"

        if self._ansible is not None:
            result = self._ansible.get("playbooks_dir", result)

        if full_path:
            result = os.path.join(self.base_dir(True), result)

        return result

    def inventories_dir(self, full_path=False):
        """
        Directory containing the inventories
        """
        result = "inventories"

        if self._ansible is not None:
            result = self._ansible.get("inventories_dir", result)

        if full_path:
            result = os.path.join(self.base_dir(True), result)

        return result

    def run_as(self):
        """
        User used to run Ansible
        """
        result = None
        if self._ansible is not None:
            result = self._ansible.get("run_as", result)
        return result

    def dynamic_inventory_file(self):
        """
        Name of the dynamic inventory script file
        """
        result = "inventory"
        if self._ansible is not None:
            result = self._ansible.get("dynamic_inventory_file", result)
        return result

    def vault_file(self):
        """
        Name of the file containing the Ansible Vault password
        """
        result = "vault.txt"
        if self._ansible is not None:
            result = self._ansible.get("vault_file", result)
        return result

    def ssh_key_file(self):
        """
        Name of the SSH private key used to connect to the remote machines
        """
        result = "access_key.pem"
        if self._ansible is not None:
            result = self._ansible.get("ssh_key_file", result)
        return result

    def exec_ansible(self):
        """
        Executable for "ansible-ansible"
        """
        result = "ansible"
        if self._ansible is not None:
            result = self._ansible.get("exec_ansible", result)
        return result

    def exec_ansible_playbook(self):
        """
        Executable for "ansible-playbook"
        """
        result = "ansible-playbook"
        if self._ansible is not None:
            result = self._ansible.get("exec_ansible_playbook", result)
        return result

    def exec_ansible_vault(self):
        """
        Executable for "ansible-vault"
        """
        result = "ansible-vault"
        if self._ansible is not None:
            result = self._ansible.get("exec_ansible_vault", result)
        return result

# vim: ft=python:ts=4:sw=4