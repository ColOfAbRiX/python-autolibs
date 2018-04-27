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

import os
import git

from execute import exec_cmd


def is_git_repo(path=None):
    """
    Checks if the current directory is part of a GIT repository
    """
    if path is None:
        path = os.getcwd()

    try:
        git_repo = git.Repo(path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        return False

    return True

def get_git_root(path=None):
    """
    Returns the root path of the GIT repository on the Current Working Directory
    """
    if path is None:
        path = os.getcwd()

    git_repo = git.Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


def exec_git(git_cmd):
    """
    Executes GIT with specific options and manages errors.
    """
    stdout, stderr, rc = exec_cmd("git %s" % git_cmd)

    if rc > 0:
        raise ScriptError("Error running command: \"git %s\"\nOutput: %s" % (git_cmd, stderr))

    return stdout

# vim: ft=python:ts=4:sw=4