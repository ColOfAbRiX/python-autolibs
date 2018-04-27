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

import logging

log_indent = 0
log_status = None

def logfunction(func):
    def _wrapper(*args, **kwargs):
        global log_indent, log_status

        indent = "  " * log_indent

        if log_status is None:
            logging.basicConfig(filename='/tmp/python-logging.log', level=logging.DEBUG)
            log_status = 1

        logging.info(indent + "Name   : %s" % func.__name__)
        logging.debug(indent + "Args #1: %s" % str(args))
        logging.debug(indent + "Args #2: %s" % str(kwargs))

        log_indent += 1
        result = func(*args, **kwargs)
        log_indent -= 1

        logging.debug(indent + "Result : %s" % str(result))

        return result

    return _wrapper

# vim: ft=python:ts=4:sw=4