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

import os
import config
from cfutils import gitutils


class PackerRepo:
    """
    Information about the Packer section of the Automation Repository
    """
    def __init__(self, repo_base=None):
        # Get repository base
        if repo_base is None and gitutils.is_git_repo(repo_base):
            repo_base = gitutils.get_git_root()

        if not gitutils.is_git_repo(repo_base):
            raise ValueError("Not a GIT repository: %s" % repo_base)

        self.repo_base = repo_base

        # Load configuration
        self._config = config.PackerConfig(self.repo_base)

        # Base path of Packer
        self.base = os.path.join(self.repo_base, self._config.base_dir())
        if not os.path.isdir(self.base):
            raise IOError("Base Packer directory doesn't exist in %s" % self.base)

    def images(self):
        """
        List of the VM images configured in packer
        """
        dirs = [x[1] for x in os.walk(self.base)][0]
        return [x for x in dirs if x not in ['cache', 'scripts']]

    def image_base(self, image):
        """
        Base path of a VM image
        """
        if image is None or image == "":
            raise ValueError("Image cannot be empty")

        image = os.path.join(self.base, image)

        if not os.path.exists(image):
            raise IOError("Image %s doesn't exist" % image)
        if not os.path.isdir(image):
            raise IOError("Image %s is not a directory" % image)

        return image

    def packer_file(self, image):
        """
        Name of the default file loaded by packer
        """
        return os.path.join(
            self.image_base(image),
            self._config.packer_file()
        )

# vim: ft=python:ts=4:sw=4