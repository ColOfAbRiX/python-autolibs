#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2016 Fabrizio Colonna <colofabrix@tin.it>
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

#
# Custom dynamic inventory script for Ansible that uses YAML to store hosts. The script
# will first load the file inventories/main.yml from the repository base.
# For more information see: https://docs.ansible.com/ansible/developing_inventory.html
#

#
# A comprehensive and simple example of an inventory that can be used is:
#
#    ---
#    # The script can import files and directories, using BASH expansion.
#    # The loading happens sequentially following the list. Nested files are
#    # merged over the parent ones.
#    import: [ 'other_file.yml', 'other_dir/', 'wildcard*' ]
#
#    # The executables described here will be executed and their YAML output
#    # be included the same way as with the "import" statement. The loading
#    # happens sequentially following the list. The items loaded with this
#    # statement overrides the "import" statement
#    executables:
#     - path: inventory-aws
#       args: ["-r eu-west-2"]
#       working_dir: "."
#       environment:  {}
#
#    # Hosts section
#    hosts:
#      - name: "vmtest01"
#        memberof: ["linux"]
#        # Name of the host. It's the only required field.
#      - name: "vmtest02"
#        # Groups that this host belongs to
#        memberof: ["redhat_7", "linux"]
#        # Variables assigned only to this host
#        vars: { custom_host_var: "Only for vmtest02" }
#
#    # Groups section
#    groups:
#     - name: "linux"
#       vars: { custom_group_var: "All linux group members" }
#       # Name of the group. It's the only required field.
#     - name: "redhat_7"
#       # The group can be member of other groups. The script
#       # avoids circular references.
#       memberof: [ "linux" ]
#       # A description for the group
#       description: "RedHat 7"
#       # Groups can be categorized to assign them a meaning
#       type: "linux_distribution"
#
#    # Global variables
#    vars:
#      global_var_1: "This variable is available to all hosts"
#      global_var_2: "And also this one"
#
# The above inventory, assuming the includes empty, generates the following
# JSON host data for Ansible when called with .get_list():
#
#     {
#       "_meta": {
#         "hostvars": {
#           "vmtest01": {
#             "custom_group_var": "All linux group members",
#             "generic": [
#               {"description": "linux", "name": "linux"},
#               {"description": "Ungrouped Hosts", "name": "ungrouped"}
#             ],
#             "global_var_1": "This variable is available to all hosts",
#             "global_var_2": "And also this one",
#             "group_types": ["generic", "linux_distribution"],
#             "linux_distribution": [{"description": "RedHat 7", "name": "redhat_7"}],
#             "memberof": ["linux"]
#           },
#           "vmtest02": {
#             "custom_group_var": "All linux group members",
#             "custom_host_var": "Only for vmtest02",
#             "generic": [
#               {"description": "linux", "name": "linux"},
#               {"description": "Ungrouped Hosts", "name": "ungrouped"}
#             ],
#             "global_var_1": "This variable is available to all hosts",
#             "global_var_2": "And also this one",
#             "group_types": ["generic", "linux_distribution"],
#             "linux_distribution": [{"description": "RedHat 7", "name": "redhat_7"}],
#             "memberof": ["redhat_7", "linux"]
#           }
#         }
#       }
#     }
#
# The script has the ability of let user override the loaded data using passing
# a YAML document as environment variable. The document will be treated as the
# last imported document and as such it has the highest priority over the others.
#


from __future__ import print_function

import glob
import time
import copy
import json
import StringIO
from repository import *
from cfutils.execute import *
from cfutils.formatting import *


class YAMLInventory(object):

    def __init__(self, yaml_file, override_yaml="", repo_info=None):
        repo_info = AnsibleRepo() if repo_info is None else repo_info
        if repo_info.base is None:
            print_c("ERROR: ", color="light_red", end='')
            print("The current directory is not a GIT repository.")
            sys.exit(1)

        local_tmp = repo_info.ans_config('defaults', 'local_tmp', '~/.ansible/tmp')

        self.ansible_group_list = []
        self.ansible_host_list  = []
        self.group_list         = []
        self.host_list          = []
        self.global_vars        = {}
        self.inventory_base     = self.detect_inventory_base(yaml_file, repo_info)
        self.yaml_file          = yaml_file
        self.cache_file         = paths_full(local_tmp, 'inventory-cache.yml')
        self.CACHE_EXPIRE       = 300
        self.override_yaml      = override_yaml

        # Load from cache only if the script has been called from the same process or
        # the cache is older than 30 minutes (inventory changes are not frequent)
        load_cache = os.path.exists(self.cache_file) and \
                     (time.time() - os.path.getmtime(self.cache_file)) < self.CACHE_EXPIRE

        # Cache is permanently disabled (not much benefits from it right now)
        load_cache = False

        if load_cache:
            try:
                # Loads the data from the cache file
                load_cache = not self._load_cache()
            except (ValueError, IOError):
                # Cache is disabled if there are issues loading it
                load_cache = False
                os.remove(self.cache_file)
                print("Error loading the cache file. Discarding cache.", file=sys.stderr)

        if not load_cache:
            """ Loading steps """

            # Load all the YAML files, starting with the main file
            self._load_yaml()

            # Adds some predefined groups common to all hosts
            self._add_default_groups()
            # Checks that all the groups referenced by hosts and groups are
            # present in the group list
            self._check_groups()
            # Adds some predefined global variables
            self._add_default_variables()

            # Converts the group data structure loaded from the YAML file into
            # the group data structure required by Ansible.
            self._create_ansible_groups()
            # Converts the host data structure loaded from the YAML file into
            # host data structure required by Ansible.
            self._create_ansible_hosts()

            # Saves the data in the cache
            self._save_cache()

    def get_list(self):
        """
        Returns the variables for one host only `--list`
        """

        # Filter the groups
        output = self.get_empty()
        for g in self.ansible_group_list:
            output[g] = {
                "hosts": self.ansible_group_list[g]["hosts"],
                "vars":  self.ansible_group_list[g]["vars"]
            }

        # Add the _meta information
        for h in self.ansible_host_list:
            output["_meta"]["hostvars"][h] = self.ansible_host_list[h]["vars"]

        return output

    def get_host(self, host):
        """ Returns the variables for one host only `--host` """
        return self.ansible_host_list.get(host, {}).get("vars", {})

    def get_hosts(self, attribute=None):
        """ CUSTOM: Returns the list of all hosts """
        if attribute is None:
            return self.host_list
        return "\n".join([x[attribute] for x in self.host_list if attribute in x])

    def get_groups(self, attribute=None):
        """ CUSTOM: Returns the list of all groups """
        if attribute is None:
            return self.group_list
        return "\n".join([x[attribute] for x in self.group_list if attribute in x])

    def detect_inventory_base(self, main_yaml_file, repo_info, opt_paths=[]):
        """
        Searches for the YAML main file in a series of default locations
        """
        # Search priority:
        #  - The specified YAML file
        #  - The directory where the script is located
        #  - The inventory directory configured for the repository
        #  - The repository root
        search_in = [
            paths_full(os.path.dirname(main_yaml_file)),
            paths_full(os.path.dirname(sys.argv[0])),
            paths_full(repo_info.base, repo_info.inventory_base),
            paths_full(repo_info.base)
        ] + opt_paths

        for where in search_in:
            full_path = paths_full(where, main_yaml_file)
            if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                return where

        raise Exception("Can't find the inventory base anywhere in %s." % search_in)

    @staticmethod
    def get_empty():
        """ Returns an empty inventory """
        return {'_meta': {'hostvars': {}}}

    @staticmethod
    def _merge_import_objs(dst, src):
        """
        Merges imported elements copying src into dest. It avoid duplications
        checking for object's names
        """
        output = copy.deepcopy(dst)
        src = copy.deepcopy(src)

        while src:
            src_item = src.pop()
            for i, dst_item in enumerate(dst):
                if dst_item['name'] == src_item['name']:
                    output[i] = merge(dst_item, src_item)
                    src_item = None
                    break

            if src_item:
                output.append(src_item)

        return output

    def _load_yaml(self):
        """ Load the whole YAML inventory """
        self.group_list, self.host_list, self.global_vars = self._load_flat(self.yaml_file)

    def _load_flat(self, file_path=None, load_list=[], use_yaml=None, is_first=True):
        """
        Loads a YAML file, including its imports, into separate instance variables.
        The data in the imported YAML files is all stored as a flat list, no hierarchy information is kept.
        """
        group_list  = []
        host_list   = []
        global_vars = {}

        if not file_path:
            file_path = self.yaml_file

        # Load in memory all the YAML data
        try:
            if use_yaml:
                fp = StringIO.StringIO(use_yaml)
            else:
                fp = open(paths_full(self.inventory_base, file_path), "r")
            yaml_docs = yaml.load_all(fp, Loader=yaml.CLoader)

            for doc in yaml_docs:
                # Check the expected format
                self._check_yaml_format(doc, file_path)

                # Load interesting keys only, ignore the others
                imports_list = doc.get("import", []) or []
                execs_list   = doc.get("executables", []) or []
                group_list   = doc.get("groups", []) or []
                host_list    = doc.get("hosts",  []) or []
                global_vars  = doc.get("vars",   {}) or {}

                # Import from files and directories
                for import_file in imports_list:
                    import_file = paths_full(self.inventory_base, import_file)

                    # Scan through BASH expansion (ignoring bad entries too)
                    for yml_file in glob.glob(import_file):
                        # Load only YAML files or directories, skip the others
                        if not os.path.isdir(yml_file):
                            if not re.match('.*\.ya?ml$', yml_file):
                                continue

                        # Avoid circular graphs
                        if yml_file in load_list:
                            continue
                        load_list.append(yml_file)

                        # Load YAML data
                        yml_file = paths_full(self.inventory_base, yml_file)

                        # Imports work both on files and directories
                        if os.path.isfile(yml_file):
                            to_import = [yml_file]
                        elif os.path.isdir(yml_file):
                            to_import = [paths_full(yml_file, i) for i in os.listdir(yml_file)]
                        else:
                            raise Exception("Can't find inventory file %s imported from %s." % (yml_file, file_path))

                        # Recursively load the data from the imports and merge the result
                        for i in to_import:
                            i_groups, i_hosts, i_vars = self._load_flat(i, load_list, use_yaml=None, is_first=False)

                            group_list  = self._merge_import_objs(group_list, i_groups)
                            host_list   = self._merge_import_objs(host_list, i_hosts)
                            global_vars = merge(global_vars, i_vars)

                # Execute the scripts and include their output
                for exec_entry in execs_list:
                    # Working directory
                    working_dir = exec_entry.get('working_dir', os.getcwd()) or os.getcwd()

                    # Environment variables
                    env = os.environ.copy()
                    env.update(exec_entry.get('environment', {}) or {})

                    # Command to execute
                    args = exec_entry.get('args', []) or []
                    exec_path = paths_full(os.path.dirname(sys.argv[0]), exec_entry['path'])
                    cmd = "%s %s" % (exec_path, ' '.join(args))

                    # Execute
                    stdout, stderr, rc = exec_cmd(cmd, cwd=working_dir, env=env)
                    if rc != 0:
                        print(stderr, file=sys.stderr)
                        continue

                    # Merge recursively the result
                    i_groups, i_hosts, i_vars = self._load_flat(i, load_list, use_yaml=stdout, is_first=False)
                    group_list  = self._merge_import_objs(group_list, i_groups)
                    host_list   = self._merge_import_objs(host_list, i_hosts)
                    global_vars = merge(global_vars, i_vars)

        except (IOError, yaml.YAMLError), exc:
            raise Exception("Error loading file file %s: %s." % (file_path, exc))

        # This is to load the custom override YAML only as a last thing and only once
        if is_first and self.override_yaml and not use_yaml:
            tmp_groups, tmp_hosts, tmp_vars = self._load_flat(None, load_list, use_yaml=self.override_yaml)

            group_list  = self._merge_import_objs(group_list, tmp_groups)
            host_list   = self._merge_import_objs(host_list, tmp_hosts)
            global_vars = merge(global_vars, tmp_vars)

        return group_list, host_list, global_vars

    def _check_yaml_format(self, doc, file_path):
        """
        Checks the format of each YAML entry, to ensure it's in the correct format
        """
        if not isinstance(doc.get("import", []) or [], list):
            raise Exception("The key 'import' must be a list, in %s." % file_path)

        if not isinstance(doc.get("executables", []) or [], list):
            raise Exception("The key 'executables' must be a list, in %s." % file_path)

        if not isinstance(doc.get("groups", []) or [], list):
            raise Exception("The key 'groups' must be a list, in %s." % file_path)

        if not isinstance(doc.get("hosts", []) or [], list):
            raise Exception("The key 'hosts' must be a list, in %s." % file_path)

        if not isinstance(doc.get("vars", {}) or {}, dict):
            raise Exception("The key 'vars' must be a dictionary, in %s." % file_path)

    def _add_default_groups(self):
        """
        Adds some predefined groups common to all hosts
        """
        self.group_list.append({
            "description": "Ungrouped Hosts",
            "name": "ungrouped",
            "type": "generic"
        })

    def _check_groups(self):
        """
        Checks that all the groups referenced by hosts and groups are present in the group list
        """
        all_groups = [group['name'] for group in self.group_list]

        for host in self.host_list:
            memberof = host.get("memberof", ["ungrouped"])

            for group_member in  memberof:
                if group_member not in all_groups:
                    raise Exception("The host '%s' can't be assigned to the group '%s' because it doesn't exist." % (
                        host['name'], group_member
                    ))

        for group in self.group_list:
            memberof = group.get("memberof", ["ungrouped"])

            for group_member in  memberof:
                if group_member not in all_groups:
                    raise Exception("The group '%s' can't be assigned to the group '%s' because it doesn't exist." % (
                        group['name'], group_member
                    ))

    def _add_default_variables(self):
        """
        Adds some predefined global variables
        """
        self.global_vars["group_types"] = []

        for g in self.group_list:
            g_name        = g["name"]                      # name is compulsory
            g_description = g.get("description", g_name) or g_name
            g_type        = g.get("type", 'generic') or 'generic'

            # Add information about all groups
            if g_type not in self.global_vars:
                self.global_vars[g_type] = []
                self.global_vars["group_types"].append(g_type)

            self.global_vars[g_type].append({
                'name': g_name,
                'description': g_description
            })

    def _create_ansible_groups(self):
        """
        Converts the group data structure loaded from the YAML file into the group data structure
        required by Ansible.
        """
        result = {}
        for g in self.group_list:
            g_name     = g["name"]                      # name is compulsory
            g_hosts    = g.get("hosts", []) or []
            g_memberof = g.get("memberof", []) or []
            g_vars     = merge(
                self.global_vars,
                g.get("vars", {}) or {}
            )

            g_vars = merge(g_vars, {
                "memberof": g_memberof
            })

            result[g_name] = {
                "hosts": g_hosts,
                "member_of": g_memberof,
                "vars": g_vars
            }

        self.ansible_group_list = result

    def _create_ansible_hosts(self):
        """
        Converts the host data structure loaded from the YAML file into host data structure
        required by Ansible.
        """
        result = {}
        for h in self.host_list:
            h_name     = h["name"]
            h_memberof = h.get("memberof", []) or []
            h_vars     = h.get("vars", {}) or {}

            # Add the hosts to the groups it belongs to and load group's variables
            g_vars = {}
            for g in h_memberof:
                self.ansible_group_list[g]["hosts"] = union([h_name], self.ansible_group_list[g]["hosts"])
                g_vars = merge(g_vars, self.ansible_group_list[g]["vars"])
            h_vars = merge(g_vars, h_vars)

            h_vars = merge(h_vars, {
                "memberof": h_memberof
            })

            result[h_name] = {
                "vars": h_vars,
                "member_of": h_memberof
            }

        self.ansible_host_list = result

    def _load_cache(self):
        """
        Loads the data from the cache file
        """
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)

        self.ansible_group_list = cache.get('group_list', {})
        self.ansible_host_list  = cache.get('host_list', {})
        self.global_vars = cache.get('global_vars', {})

        # Returns true if all data has been loaded
        return self.ansible_group_list and self.ansible_host_list and self.global_vars

    def _save_cache(self):
        """
        Saves the data in the cache
        """
        data = {
            'group_list':  self.ansible_group_list,
            'host_list':   self.ansible_host_list,
            'global_vars': self.global_vars
        }

        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

# vim: ft=python:ts=4:sw=4