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

from __future__ import print_function

import sys
import json
import argparse
import tempfile


from autolibs.utils.execute import *
from autolibs.packer.tools import *
from autolibs.terraform.repository import TerraformRepo


def centos7_aws_minimal(raw_data, args):
    """
    Data for the image centos7-aws-minimal
    """
    result = credentials(raw_data, args.aws_region, args.packer_user)
    result.update(config_minimal(raw_data))
    result.update(centos_release(raw_data))
    return result


def centos7_aws_base(raw_data, args):
    """
    Data for the image centos7-aws-base
    """
    result = credentials(raw_data, args.aws_region, args.packer_user)
    result.update(config_base(raw_data, args.environment))
    result.update(ansible(raw_data))
    result.update(centos_release(raw_data))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target_image',
        action='store',
        default=None,
        choices=[
            "centos7-aws-minimal",
            "centos7-aws-base"
        ],
        help="Target packer image to build."
    )
    parser.add_argument(
        'environment',
        action='store',
        default=None,
        help="Target environment."
    )
    parser.add_argument(
        'aws_region',
        action='store',
        default=None,
        choices=[
            "eu-west-2",
        ],
        help="Target AWS region."
    )
    parser.add_argument(
        'packer_user',
        action='store',
        nargs='?',
        default='packer',
        help="User used by packer."
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help="Just show the command that would be run."
    )
    args = parser.parse_args()

    try:
        terraform_repo = TerraformRepo()
    except (ValueError, IOError, LookupError) as e:
        print_c("ERROR! ", color="light_red", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    # Read all raw data
    state_file = terraform_repo.state_file(args.environment)
    with open(state_file) as data_file:
        raw_data = json.load(data_file)

    # Load the appropriate data
    if args.target_image == "centos7-aws-minimal":
        variables = centos7_aws_minimal(raw_data, args)

    elif args.target_image == "centos7-aws-base":
        variables = centos7_aws_base(raw_data, args)

    else:
        raise EnvironmentError("Couldn't find the image %s" % args.target_image)

    # Go, pack!
    run_packer(variables, args.target_image, args.dry_run)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4