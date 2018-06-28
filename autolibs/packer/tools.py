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

import re
import json
import tempfile

from autolibs.utils.execute import *
from autolibs.packer.repository import PackerRepo


def run_packer(config, image, dry_run=False):
    repo = PackerRepo()

    with tempfile.NamedTemporaryFile() as var_file:
        # Write the configuration in a temporary JSON file
        json.dump(config, var_file)
        var_file.flush()

        # The packer command to execute
        packer_cmd = "%s build --var-file %s %s" % (
            get_bin_path("packer"),
            var_file.name,
            repo.packer_file(image)
        )

        # Run and switch to packer
        if dry_run:
            print(packer_cmd)
        else:
            switch_cmd(packer_cmd, cwd=repo.image_base(image))


def tfstate_resource(tfstate, resource_regex):
    """
    Returns the attribute of resource found in a .tfstate file
    """
    return tfstate_resources(tfstate, resource_regex)[resource_regex]


def tfstate_resources(tfstate, *resource_regexes):
    """
    Returns the attribute of resource found in a .tfstate file
    """
    result = {}

    for module in tfstate['modules']:
        for res_name, res_content in module['resources'].iteritems():
            for regex in resource_regexes:
                if re.search(regex, res_name):
                    result.update({
                        regex: res_content['primary']['attributes']
                    })

    return result


def credentials(raw_data, aws_region, packer_user):
    """
    Returns information about credentials to connect to AWS
    """
    resource = r"aws_iam_access_key\." + packer_user
    aws_iam_access_key = tools.tfstate_resource(raw_data, resource)
    return {
        "aws_access_key": aws_iam_access_key.get('id', None),
        "aws_secret_key": aws_iam_access_key.get('secret', None),
        "aws_region": aws_region
    }


def centos_release(raw_data):
    """
    Returns information about the CentOS image to download
    TODO: This must not be hard coded
    """
    return {
        "image_name": "CentOS-7.3.1611-x86_64",
        "iso_url": "http://mirror.as29550.net/mirror.centos.org/7/isos/x86_64/CentOS-7-x86_64-DVD-1611.iso",
        "iso_checksum": "c455ee948e872ad2194bdddd39045b83634e8613249182b88f549bb2319d97eb"
    }


def config_minimal(raw_data):
    """
    Returns information about the various configuration options for the MINIMAL
    installation
    """
    ami_import_bucket = tools.tfstate_resource(
        raw_data,
        r"aws_s3_bucket\.ami_import_bucket"
    )
    return {
        's3_import_bucket': ami_import_bucket.get('id', None)
    }


def config_base(raw_data, environment):
    """
    Returns information about the various configuration options for the BASE
    installation
    """
    result = tools.tfstate_resources(
        raw_data,
        r"aws_security_group\.outbound_all",
        r"aws_security_group\.inbound_all",
        r"aws_vpc\.default",
        r"aws_subnet\.tier_2\.0"
    )

    return {
        'security_group_ids': ",".join([
            result[r"aws_security_group\.outbound_all"]["id"],
            result[r"aws_security_group\.inbound_all"]["id"],
        ]),
        'vpc_id': result[r"aws_vpc\.default"]["id"],
        'subnet_id': result[r"aws_subnet\.tier_2\.0"]["id"],
        'environment': environment,
    }


def ansible(raw_data):
    """
    Returns information about the Ansible setup for Packer
    TODO: This must not be hardcoded
    """
    return {
        "ansible_user": "centos",
        "ansible_sudo_pass": "centos"
    }


# vim: ft=python:ts=4:sw=4