#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        if repo_base is None or not is_git_repo(repo_base):
            raise ValueError("Not a GIT repository: %s" % repo_base)
        self._repo_base = repo_base

        self.config_file = os.path.join(self._repo_base, self.config_file())

        # Configuration section
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if "ansible" not in self.config.sections():
            raise LookupError("Ansible configuration section doesn't exist in %s." % self.config_file)

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
        base_dir = self._ansible.get("base_dir", "ansible")
        if full_path:
            base_dir = os.path.join(self._repo_base, base_dir)
        return base_dir

    def roles_dir(self, full_path=False):
        """
        Directory containing the roles
        """
        roles_dir = self._ansible.get("roles_dir", "roles")
        if full_path:
            roles_dir = os.path.join(self._repo_base, roles_dir)
        return roles_dir

    def playbooks_dir(self, full_path=False):
        """
        Directory containing the playbooks
        """
        playbooks_dir = self._ansible.get("playbooks_dir", "playbooks")
        if full_path:
            playbooks_dir = os.path.join(self._repo_base, playbooks_dir)
        return playbooks_dir

    def inventories_dir(self, full_path=False):
        """
        Directory containing the inventories
        """
        inventories_dir = self._ansible.get("inventories_dir", "inventories")
        if full_path:
            inventories_dir = os.path.join(self._repo_base, inventories_dir)
        return inventories_dir

    def run_as(self):
        """
        User used to run Ansible
        """
        return self._ansible.get("run_as", None)

    def dynamic_inventory_file(self):
        """
        Name of the dynamic inventory script file
        """
        return self._ansible.get("dynamic_inventory_file", "inventory")

    def vault_file(self):
        """
        Name of the file containing the Ansible Vault password
        """
        return self._ansible.get("vault_file", "vault.txt")

    def ssh_key_file(self):
        """
        Name of the SSH private key used to connect to the remote machines
        """
        return self._ansible.get("ssh_key_file", "access_key.pem")

    def exec_ansible(self):
        """
        Executable for "ansible-ansible"
        """
        return self._ansible.get("exec_ansible", "ansible")

    def exec_ansible_playbook(self):
        """
        Executable for "ansible-playbook"
        """
        return self._ansible.get("exec_ansible_playbook", "ansible-playbook")

    def exec_ansible_vault(self):
        """
        Executable for "ansible-vault"
        """
        return self._ansible.get("exec_ansible_vault", "ansible-vault")

# vim: ft=python:ts=4:sw=4