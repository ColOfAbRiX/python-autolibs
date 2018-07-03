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
# Information about an Ansible repository
#

from __future__ import print_function

import re
import os
import sys
import yaml
import glob
from ansible import constants as C
from autolibs.ansible import config
from autolibs.utils import gitutils
from autolibs.utils.common import *
from autolibs.utils.execute import *
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class AnsibleRepo:
    """
    Information about an Ansible repository
    """

    def __init__(self, repo_base=None):
        # Get repository base
        if repo_base is None and gitutils.is_git_repo(repo_base):
            repo_base = gitutils.get_git_root()

        if not gitutils.is_git_repo(repo_base):
            raise ValueError("Not a GIT repository: %s" % repo_base)

        self.repo_base = repo_base

        # Load configuration
        self._config = config.AnsibleConfig(self.repo_base)

        # Base path of Ansible
        self.base = os.path.join(self.repo_base, self._config.base_dir())
        if not os.path.isdir(self.base):
            raise IOError("Base Ansible directory doesn't exist in %s" % self.base)

        self._load_ansible_config()
        self._set_executables()

        # Buffers
        self._tags      = None
        self._playbooks = None
        self._vaults    = None

        # Base paths
        self.roles_base     = paths_full(self.base, self._config.roles_dir())
        self.playbooks_base = paths_full(self.base, self._config.playbooks_dir())
        self.inventory_base = paths_full(self.base,
            self.ans_config('defaults', 'inventory', '/etc/ansible/hosts')
        )

        # Others
        self.run_as         = self._config.run_as()
        self.vault_file     = self._config.vault_file()
        self.ssh_key        = self._config.ssh_key_file()
        self.dynainv_file   = self._config.dynamic_inventory_file()
        # Default path where to search for the dynamic inventory
        self.dynainv_path   = paths_full(
            self.base,
            "scripts",
            self.dynainv_file
        )

    def _load_ansible_config(self):
        """
        Loads a reference to the Ansible configuration file
        """
        old_cwd = os.getcwd()
        os.chdir(self.base)
        self._p, _ = C.load_config_file()
        os.chdir(old_cwd)

    def _set_executables(self):
        """
        Sets the ansible executables configuration
        """
        opt_dirs = ["/usr/local/bin", "/usr/bin", "/usr/local/sbin", "/usr/sbin:/bin"]
        self.ansible = get_bin_path(
            os.environ.get('ANSIBLE', self._config.exec_ansible()),
            opt_dirs=opt_dirs
        )
        self.ansible_playbook = get_bin_path(
            os.environ.get('ANSIBLE_PLAYBOOK', self._config.exec_ansible_playbook()),
            opt_dirs=opt_dirs
        )
        self.ansible_vault = get_bin_path(
            os.environ.get('ANSIBLE_VAULT', self._config.exec_ansible_vault()),
            opt_dirs=opt_dirs
        )

    def ans_config(self, section, name, default):
        """
        Gets an Ansible configuration using the repository's ansible.cfg if present
        """
        env_var = "ANSIBLE_%s" % name.upper()
        return C.get_config(self._p, section, name, env_var, default)

    def playbooks(self):
        """
        Finds all the playbook of the repository
        """
        if self._playbooks is not None:
            return self._playbooks

        self._playbooks = []

        for root, _, files in os.walk(self.playbooks_base, topdown=False):
            if '.git' in root:
                continue

            for name in files:
                name = paths_full(root, name)

                if not re.findall(r'\.ya?ml$', name, re.IGNORECASE):
                    continue

                self._playbooks.append(name)

        return self._playbooks

    def vaulted(self):
        """
        Finds all the vaulted files of the repository
        """
        if self._vaults is not None:
            return self._vaults

        self._vaults = []

        for root, _, files in os.walk(self.base, topdown=False):
            if '.git' in root:
                continue

            for name in files:
                name = paths_full(root, name)
                try:
                    with open(name) as f:
                        if re.findall(r'^\$ANSIBLE_VAULT;[^;]+;[^;]+$', str(f.readline())):
                            self._vaults.append(name)
                except (OSError, IOError):
                    continue

        return self._vaults

    def tags(self):
        """
        Lists all the tags of the repository
        """
        if self._tags is not None:
            return self._tags

        self._tags = []

        for task_file in glob.glob(paths_full(self.roles_base, "*/tasks/*.yml")):
            try:
                with open(task_file, "r") as f:
                    doc = yaml.load(f)
                    # Check it's proper Ansible-YAML
                    if not isinstance(doc, (list, )):
                        continue
            except (OSError, IOError, yaml.YAMLError):
                continue

            for task in doc:
                tags = task.get("tags", [])
                if not isinstance(tags, list):
                    tags = [tags]
                self._tags.extend(tags)

        self._tags = sorted(list(set(self._tags)))
        return self._tags

# vim: ft=python:ts=4:sw=4