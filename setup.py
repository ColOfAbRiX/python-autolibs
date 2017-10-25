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
        check_call("ln -fs /usr/bin/register-deploy /etc/profile.d/register-deploy.sh".split())
        check_call("ln -fs /usr/bin/register-vault /etc/profile.d/register-vault.sh".split())
        check_call("ln -fs /usr/bin/vault /usr/bin/vault-host".split())
        check_call("ln -fs /usr/bin/vault /usr/bin/vault-group".split())
        check_call("mkdir -p /opt/autolibs-hooks".split())
        check_call("cp -f bin/git-hooks/* /opt/autolibs-hooks", shell=True)
        install.run(self)
        # To clean the above, run:
        #   rm -f /etc/profile.d/register-deploy.sh
        #   rm -f /etc/profile.d/register-vault.sh
        #   rm -f /usr/bin/vault-host
        #   rm -f /usr/bin/vault-group
        #   rm -rf /opt/autolibs-hooks


setup(
    name='autolibs',
    version='1.0',
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
    scripts=[
        # Ansible
        'bin/deploy',
        'bin/inventory',
        'bin/vault',
        # Ansible autocomplete
        'bin/ac/register-deploy',
        'bin/ac/support-deploy.py',
        'bin/ac/register-vault',
        'bin/ac/support-vault.py',
        # Packer
        'bin/packer_minimal',
    ],
    cmdclass={
        'install': PostInstallCommand
    },
)

# vim: ft=python:ts=4:sw=4