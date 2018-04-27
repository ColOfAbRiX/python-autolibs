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
import shlex
import getpass
import subprocess as sp
from common import ScriptError


def paths_full(*chunks):
    """
    Joins together chunks of a path and return the absolute, clean path
    """
    res = ""

    for path in chunks:
        if path.startswith(os.path.pathsep):
            res = path
        else:
            res = os.path.join(res, path)

    if '~' in res:
        res = os.path.expanduser(res)
    elif not res.startswith(os.path.pathsep):
        res = os.path.abspath(res)

    return res.replace('/./', '/')


def get_bin_path(arg, opt_dirs=[]):
    """
    Find system executable in PATH.
    """
    sbin_paths = ['/sbin', '/usr/sbin', '/usr/local/sbin']
    paths = []
    for d in opt_dirs:
        if d is not None and os.path.exists(d):
            paths.append(d)

    paths += os.environ.get('PATH', '').split(os.pathsep)
    bin_path = None

    # mangle PATH to include /sbin dirs
    for p in sbin_paths:
        if p not in paths and os.path.exists(p):
            paths.append(p)

    for d in paths:
        if not d:
            continue
        path = os.path.join(d, arg)
        if os.path.exists(path) and not os.path.isdir(path) and os.access(path, os.X_OK):
            bin_path = path
            break

    return bin_path


def switch_cmd(command, run_as=None, cwd=None, env=[]):
    """
    Executes a command switching the current process
    """

    # Change working directory
    if cwd is None:
        cwd = os.getcwd()
    os.chdir(cwd)

    # Set environment
    os.environ.update(env)
    env = os.environ.copy()

    # Check if sudo
    current_user = getpass.getuser()
    if run_as is not None and run_as not in [current_user, '']:
        command = "%s -Esu %s -- %s" % (get_bin_path("sudo"), run_as, command)

    command = shlex.split(command)
    os.execv(command[0], command)


def exec_cmd(command, run_as="", cwd=None, env=None, async=False):
    """
    Executes a system command as a specific user
    """

    # Change environment and working directory
    if env is None:
        env = os.environ.copy()
    if cwd is None:
        cwd = os.getcwd()
    env['PWD'] = cwd

    # Check if sudo
    current_user = getpass.getuser()
    if run_as not in [current_user, '']:
        command = "%s -su %s -- %s" % (get_bin_path("sudo"), run_as, command)

    p = sp.Popen(command, shell=True, cwd=cwd, env=env, stdout=sp.PIPE, stderr=sp.PIPE)

    # Managing output
    if async:
        return p
    p.wait()
    return (p.stdout.read().strip(), p.stderr.read().strip(), p.returncode)


# vim: ft=python:ts=4:sw=4