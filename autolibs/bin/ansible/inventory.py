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
# inventory - Dynamic inventory script to store configuration in YAML files
#

from __future__ import print_function

import sys
import argparse
from cfutils.formatting import *
from autolibs.ansible.inventory import *
from autolibs.ansible.repository import *


def inventory(args):
    main_yaml = os.environ.get('INVENTORY_MAIN', "main.yml")
    if args.main is not None:
        main_yaml = args.main

    # The user can add a high-priority YAML code that is imported last
    override = os.environ.get('INVENTORY_OVERRIDE', '')

    try:
        # Get the appropriate information from the inventory
        if args.list:
            output = YAMLInventory(main_yaml, override_yaml=override).get_list()
            p_json(output)

        elif args.host:
            output = YAMLInventory(main_yaml, override_yaml=override).get_host(args.host)
            p_json(output)

        elif args.list_hosts != '' or args.list_groups != '':
            inventory = YAMLInventory(main_yaml, override_yaml=override)

            # Display hosts
            if args.list_hosts is None:
                p_json(inventory.get_hosts(args.list_hosts))
            elif args.list_hosts != '':
                print(inventory.get_hosts(args.list_hosts))

            # Display groups
            if args.list_groups is None:
                p_json(inventory.get_groups(args.list_groups))
            elif args.list_groups != '':
                print(inventory.get_groups(args.list_groups))

        else:
            output = YAMLInventory.get_empty()
            p_json(output)

    except (ValueError, IOError, LookupError) as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)


def main():
    # Command line arguments
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--list',
        action='store_true',
        help="Complete inventory, data as per Ansible specifications."
    )
    group.add_argument(
        '--host',
        action='store',
        help="Data for a single host, as per Ansible specifications."
    )
    simple = group.add_argument_group()
    simple.add_argument(
        '--list-hosts', '-l',
        action='store',
        nargs='?',
        default="",
        help="Simple list of hosts, with information."
    )
    simple.add_argument(
        '--list-groups', '-g',
        action='store',
        nargs='?',
        default="",
        help="Simple list of groups, with information."
    )

    parser.add_argument(
        '--main', '-y',
        action='store',
        help=("The main YAML file to load. This is useful for debugging, as "
              "Ansible doesn't specify a main file. The main file can can be "
              "specified also with the environment variable INVENTORY_MAIN.")
    )

    try:
        inventory(parser.parse_args())

    except ScriptError as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4