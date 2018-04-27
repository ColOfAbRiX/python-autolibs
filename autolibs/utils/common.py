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
import crypt
import random
import string
import urllib2
from operator import *
from itertools import *
try:
    import json
except ImportError:
    import simplejson as json


class ScriptError(Exception):
    """
    Exceptions raised by scripts
    """
    def __init__(self, message, *args):
        self.message = message
        super(ScriptError, self).__init__(message, *args)


def funcall_info(frame):
    """
    Display name, argument and their values of a function call
    """
    args, _, _, values = inspect.getargvalues(frame)
    print(
        'Called "%s" with arguments (%s)' % (
            inspect.getframeinfo(frame)[2],
            ', '.join(map(lambda n: "%s=%s" % (n, str(values[n])), args))
        )
    )
    return [(i, values[i]) for i in args]


def flatmap(f, items):
    return list(chain.from_iterable(imap(f, items)))


def group_by(data, group_by=[], **aggregators):
    """
    SQL-like group by function.
    """
    result = []
    grouper = itemgetter(*group_by)

    for key, grp in groupby(sorted(data, key=grouper), grouper):
        if not isinstance(key, tuple):
            key = (key, )

        # Groupby key
        partial = dict(zip(group_by, key))

        # Aggregators
        grp = list(grp)
        for field, function in aggregators.iteritems():
            partial[field] = function(grp)

        result.append(partial)

    return result


def build_regex(pattern, pattern_name=None, **kwargs):
    """
    Return regex string as a named capture group.
    See: https://tonysyu.github.io/readable-regular-expressions-in-python.html
    """
    pattern = pattern.format(**kwargs)

    if pattern_name is not None:
        return r'(?P<{name}>{pattern})'.format(name=pattern_name, pattern=pattern)

    return pattern


def union(a, b):
    """
    Return the union of two lists
    """
    if not isinstance(a, list) and isinstance(b, list):
        return b
    if isinstance(a, list) and not isinstance(b, list):
        return a
    if not isinstance(a, list) and not isinstance(b, list):
        return []

    result = []

    a.extend(b)
    for x in a:
        if x not in result:
            result.append(x)

    return result


def merge(a, b):
    """
    Recursively merges hash b into a so that keys from b take precedence over keys from a
    See: https://github.com/ansible/ansible/blob/6787fc70a643fb6e2bdd2c6a6202072d21db72ef/lib/ansible/utils/vars.py
    """

    # if a is empty or equal to b, return b
    if a == {} or a == b:
        return b.copy()

    # if b is empty the below unfolds quickly
    result = a.copy()

    # next, iterate over b keys and values
    for k, v in b.iteritems():
        # if there's already such key in a
        # and that key contains a MutableMapping
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            # merge those dicts recursively
            result[k] = merge(result[k], v)
        else:
            # otherwise, just copy the value from b to a
            result[k] = v

    return result


def random_string(N):
    """ Returns a random string of ASCII characters """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_letters + string.digits
        ) for _ in range(N)
    )


def sha512_crypt(password, rounds):
    """
    Encrypts a password for Linux shadow file
    See: https://stackoverflow.com/questions/34463134/sha-512-crypt-output-written-with-python-code-is-different-from-mkpasswd
    """
    rounds = max(1000, min(999999999, rounds or 5000))
    prefix = '$6$rounds={0}$'.format(rounds)
    return crypt.crypt(password, prefix + random_string(8))


def rest_request(url, data={}):
    """
    Makes a REST call to the server optionally sending JSON data
    """
    try:
        data = json.load(
            urllib2.urlopen(url, data=json.dumps(data), timeout=5)
        )
    except (urllib2.HTTPError, urllib2.URLError, ValueError) as e:
        raise ScriptError(e.message)

    return data


# vim: ft=python:ts=4:sw=4