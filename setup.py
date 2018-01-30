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

import os
import sys

from setuptools import setup
from subprocess import check_call
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call("ln -fs $(which register-deploy.sh) /etc/profile.d/register-deploy.sh", shell=True)
        check_call("ln -fs $(which register-vault.sh) /etc/profile.d/register-vault.sh", shell=True)
        install.run(self)
        # To clean the above, run:
        #   rm -f /etc/profile.d/register-deploy.sh
        #   rm -f /etc/profile.d/register-vault.sh


setup(
    name='autolibs',
    version='1.3.4',
    author='Fabrizio Colonna',
    author_email='colofabrix@tin.it',
    url='https://github.com/ColOfAbRiX',
    description='Python Automation Tools',
    long_description=open('README.md').read(),
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'cfutils',
        'configparser2',
        'ansible >=2.0.0, <2.4.0'
    ],
    cmdclass={
        'install': PostInstallCommand
    },
    entry_points = {
        'console_scripts': [
            'deploy=autolibs.bin.ansible.deploy:main',
            'inventory=autolibs.bin.ansible.inventory:main',
            'inventory-aws=autolibs.bin.ansible.inventoryaws:main',
            'vault-host=autolibs.bin.ansible.vault:main',
            'vault-group=autolibs.bin.ansible.vault:main',
            'packit=autolibs.bin.packer.packit:main',
            'support-deploy=autolibs.bin.ansible.supportdeploy:main',
            'support-vault=autolibs.bin.ansible.supportvault:main',
            'pre-commit=autolibs.githooks.precommit:main',
            'pre-push=autolibs.githooks.prepush:main',
            'commit-msg=autolibs.githooks.commitmsg:main',
        ],
    },
    scripts=[
        'bin/register-deploy.sh',
        'bin/register-vault.sh',
    ],
)

# vim: ft=python:ts=4:sw=4