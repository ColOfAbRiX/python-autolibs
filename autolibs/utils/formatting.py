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
import sys
import math
try:
    import json
except ImportError:
    import simplejson as json
try:
    import colored
    __colored__ = True
except ImportError:
    __colored__ = False


def print_c(text, color=None, **kwargs):
    """
    Prints using colors.
    """
    if __colored__ and color is not None and sys.stdout.isatty():
        print(colored.fg(color), end='')
        print(text, **kwargs)
        print(colored.attr("reset"), end='')

    else:
        print(text, **kwargs)

    sys.stdout.flush()


def p_json(data, color=None):
    """
    Prints a formatted JSON to the output
    """
    if sys.stdout.isatty():
        print_c(format_json(data), color)

    else:
        print(json.dumps(data, separators=(',', ':')))


def format_json(data):
    """
    Returns a human-formatted JSON
    """
    return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))


def format_timedelta(seconds, lookup=None, sep=', '):
    """
    Formats a timedelta into a human readable expanded format with a precusion up to microsecond
    """
    if lookup is None:
        loopkup = [
            {'divider': 1,    'format': '{0:.0f} {1}', 'unit': 'us',   'units': 'us',     'value': None},
            {'divider': 1000, 'format': '{0:.0f} {1}', 'unit': 'ms',   'units': 'ms',     'value': 0},
            {'divider': 1000, 'format': '{0:.0f} {1}', 'unit': 'sec',  'units': 'secs',   'value': 0},
            {'divider': 60,   'format': '{0:.0f} {1}', 'unit': 'min',  'units': 'mins',   'value': 0},
            {'divider': 60,   'format': '{0:.0f} {1}', 'unit': 'hour', 'units': 'hours',  'value': 0},
            {'divider': 24,   'format': '{0:.0f} {1}', 'unit': 'day',  'units': 'days',   'value': 0},
            {'divider': 7,    'format': '{0:.0f} {1}', 'unit': 'week', 'units': 'weeks',  'value': 0},
            {'divider': 4.348214, 'format': '{0:.0f} {1}', 'unit': 'month', 'units': 'months', 'value': 0},
            {'divider': 12,   'format': '{0:.0f} {1}', 'unit': 'year',  'units': 'years', 'value': 0},
        ]

    for i, current in enumerate(loopkup):
        if i == 0:
            current.update({'value': round(seconds * 1E+6)})
        else:
            previous = loopkup[i - 1]
            current.update({'value': math.floor(previous['value'] / current['divider'])})
            previous.update({'value': previous['value'] - current['value'] * current['divider']})

    output = ""
    for entry in loopkup:
        if entry['value'] != 0:
            unit   = entry['unit'] if entry['value'] == 1 else entry['units']
            entry  = entry['format'].format(entry['value'], unit)
            output = entry if output == "" else entry + sep + output

    if output == "":
        return "0s"

    return output


def format_filesize(num, suffix='B'):
    """
    See: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0

    return "%.1f%s%s" % (num, 'Yi', suffix)


# vim: ft=python:ts=4:sw=4