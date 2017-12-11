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
# deploy.py - Configuration of an Ansible deployment
#

from __future__ import print_function

import time
import uuid
import json

from stat import *
from cfutils.common import *
from cfutils.execute import *
from cfutils.formatting import print_c


class DeployConfig:

    def __init__(self, repo_info, playbook_file, target, filter, kwargs=[]):

        # Load all the variables that configure the deployment
        self._set_playbook(repo_info, playbook_file)
        self._set_inventory(repo_info, target)
        self._set_vault(repo_info, target)
        self._set_ssh_key(repo_info, target)

        # Add vault if needed
        self.common_args = ""
        if len(repo_info.vaulted()) > 0:
            if self.vault_file is not None:
                self.common_args += " --vault-password-file=%s" % self.vault_file
            else:
                self.common_args += " --ask-vault-pass"

        # Add SSH key if present
        if self.ssh_key:
            self.common_args += " --private-key %s" % self.ssh_key

        # Inventory
        self.common_args += " -i %s" % self.inventory

        # Additional filters
        if filter is not None:
            self.common_args += " -l %s" % filter

        # Basic deploy.py command
        self.deploy_base = (repo_info.ansible_playbook + self.common_args).strip()

        # Deploy command with user arguments
        self.deploy_full = "%s %s %s" % (self.deploy_base, self.playbook, ' '.join(kwargs))
        self.deploy_full = self.deploy_full.strip()

    def _set_playbook(self, repo_info, playbook_file):
        """
        Sets the plabook file configuration
        """
        self.playbook_file = playbook_file
        self.playbook = paths_full(repo_info.playbooks_base, playbook_file)

        # Check the playbook exists
        if not os.path.isfile(self.playbook):
            raise ScriptError("Can't find the playbook file \"%s\"." % self.playbook)

    def _set_inventory(self, repo_info, target):
        """
        Sets the inventory files and configuration, looking for it in several different places
        """
        self.inventory = None

        # Search priority:
        #  - The <target> in the inventory directory
        #  - The file hosts in the inventory/<target> directory
        #  - The dynamic script in inventory/<target>
        #  - The dynamic script in the default dynamic script location
        search_in = [
            target,
            os.path.join(target, target),
            os.path.join(target, "hosts"),
            os.path.join(target, repo_info.dynainv_file),
            repo_info.dynainv_path,
        ]
        search_in = [paths_full(repo_info.base, repo_info.inventory_base, x) for x in search_in]

        for where in search_in:
            if not os.path.isfile(where):
                where += ".ini"
                if not os.path.isfile(where):
                    continue

            if os.access(where, os.X_OK):
                self.use_dynamic = True
                self.inventory   = where
                break
            elif os.access(where, os.R_OK):
                self.use_dynamic = False
                self.inventory   = where
                break

        if self.inventory is None:
            raise ScriptError("Can't find the inventory file anywhere in %s." % search_in)

    def _set_vault(self, repo_info, target):
        """
        Sets the configuration for using vaulted files
        """
        self.vault_file = None

        # Search priority:
        #  - inventory/<target>/vault.txt
        #  - inventory/vault.txt
        #  - <repository root>/vault.txt
        search_in = [
            os.path.join(repo_info.inventory_base, target),
            repo_info.inventory_base,
            "",
        ]
        search_in = [paths_full(repo_info.base, x, repo_info.vault_file) for x in search_in]

        for where in search_in:
            if not os.path.isfile(where):
                continue

            # Ensuring strict permissions
            if os.stat(where).st_mode & (S_IWGRP | S_IWOTH | S_IROTH):
                print("Found a potential vault file in %s, but it has unsecure permissions." % where)
                continue

            if os.access(where, os.R_OK):
                self.vault_file = where
                break

    def _set_ssh_key(self, repo_info, target):
        """
        Sets the configuration for using an SSH key
        """
        self.ssh_key = None

        # Search priority:
        #  - inventory/<target>/access_key.pem
        #  - inventory/access_key.pem
        #  - <repository root>/access_key.pem
        search_in = [
            os.path.join(repo_info.inventory_base, target),
            repo_info.inventory_base,
            "",
        ]
        search_in = [paths_full(repo_info.base, x, repo_info.ssh_key) for x in search_in]

        for where in search_in:
            if not os.path.isfile(where):
                continue

            # Ensuring strict permissions
            if os.stat(where).st_mode & (S_IWGRP | S_IWOTH | S_IROTH):
                print("Found a potential SSH key file in %s, but it has unsecure permissions." % where)
                continue

            if os.access(where, os.R_OK):
                self.ssh_key = where
                break

# vim: ft=python:ts=4:sw=4