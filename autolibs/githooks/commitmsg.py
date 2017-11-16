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

from __future__ import print_function

import re
import sys

from cfutils.common import *
from cfutils.execute import *
from cfutils.gitutils import *
from cfutils.formatting import print_c


def commit_msg(commit_msg):
    #
    # Message content
    #

    # Check only the first line
    commit_msg = commit_msg.split('\n', 1)[0]

    print_c(" Repository", color='white')
    print_c("-" * 40, color='white')

    print_c("Commit message checks:")
    print_c("  Check message reference... ", end='')

    # Message
    message = build_regex("[^\.]{{8,}}")

    # Tickets: "EP01351699: Ticket completed."
    ticket_token = build_regex("[A-Z]{{2}}[0-9]{{8}}", pattern_name="ticket")
    ticket = build_regex(
        "{ticket_token}:\s+{message}\.",
        pattern_name="ticket_title", ticket_token=ticket_token, message=message
    )

    # JIRA Cards: "JIRATAG-10: This is a commit. JIRATAG-10: This is another commit."
    card_token = build_regex("[A-Z]+-[0-9]+", pattern_name="card")
    card = build_regex(
        "{card_token}:\s+{message}\.",
        pattern_name="card_name", card_token=card_token, message=message
    )

    # Notes: "NOTES: This is a note on the commit."
    note_token = build_regex("NOTES?")
    note = build_regex(
        "{note_token}:\s+{message}\.",
        pattern_name="note_content", note_token=note_token, message=message
    )

    # Test: "TEST: This is a test."
    test_token = build_regex("TESTS?")
    test = build_regex(
        "{test_token}:\s+{message}\.",
        pattern_name="test_content", test_token=test_token, message=message
    )

    # Caveats: "CAVEAT: When reading note that something is not perfect."
    caveat_token = build_regex("CAV(|EATS?)")
    caveat = build_regex(
        "{caveat_token}:\s+{message}\.",
        pattern_name="caveat_content", caveat_token=caveat_token, message=message
    )

    # Releases: "v1.2.3: Next release ready."
    release_version = build_regex("[vV]?[0-9]+(\.[0-9]+){{,2}}", pattern_name="release_version")
    release = build_regex(
        "{release_ver}:\s+{message}\.",
        pattern_name="release", release_ver=release_version, message=message
    )

    # Final regex
    message_regex = build_regex(
        "^({release}|{ticket}|{card}|{test})(|\s+{note})(|\s+{caveat})$",
        release=release, ticket=ticket, card=card, note=note, test=test, caveat=caveat
    )
    message_info = re.search(message_regex, commit_msg)
    message_info = {} if message_info is None else message_info.groupdict()

    # Check if this is a merge commit
    is_merge = re.match(r'^Merge.+branch.+into.+$', commit_msg, re.IGNORECASE) is not None

    # Check the text of the commit
    if not message_info and not is_merge:
        print_c("ERROR", color="light_red")
        print(
            "\nBad commit message\n\n"
            "The commit message doesn't comply to\n"
            "the required standard.\n\n"
            "Commit messages must be short and clear\n"
            "descriptions of the changes on the last\n"
            "commit and they must have a reference\n"
            "to a card or a ticket. Messages can\n"
            "contain notes, caveats, test comments.\n\n"
            "Merge commits are also possibile using\n"
            "the default text given by GIT.\n\n"
            "Example of valid messages are:\n"
            "  TEST: This is a test.\n"
            "  CARD-10: This is a commit.\n"
            "  AA12345678: Ticket completed.\n"
            "  CAVEAT: Something is not perfect.\n"
            "  NOTES: This is a note on the commit.\n\n"
            "Change the commit message and try again.\n"
        )
        return False
    print_c("OK", color='light_green')

    #
    # GIT Branch
    #
    if not is_merge:
        print_c("  Check branch name... ", end='')

        git_branch = re.search(r'\s*\*\s+(.*)', exec_git('branch'), re.MULTILINE).group(1).strip()

        # Branch type
        branch_type = build_regex("(feature|bugfix|hotfix|ticket|release)", pattern_name="type")

        # Final regex
        branch_regex = build_regex(
            "{branch_type}/({card_token}|{release_version}|{ticket_token})",
            branch_type=branch_type, card_token=card_token, release_version=release_version, ticket_token=ticket_token
        )

        branch_info = re.search(branch_regex, git_branch)
        branch_info = {} if branch_info is None else branch_info.groupdict()

        if not branch_info:
            print_c("ERROR", color="light_red")
            print(
                "\nBad branch name\n\n"
                "The current branch doesn't comply with\n"
                "the required standard.\n\n"
                "The name of the branch must reflect\n"
                "the type of branch and it must contain\n"
                "a reference to an issue tracker like\n"
                "JIRA, OTRS or similar.\n\n"
                "Rename the current branch.\n"
            )
            return False

        # Check that the commit reflect the branch name
        branch_type = branch_info.get('type', '')
        branch_match = message_match = None

        if branch_type in ["feature", "bugfix", "hotfix"]:
            branch_match = branch_info['card']
            message_match = message_info['card']

        elif branch_type == "ticket":
            branch_match = branch_info['ticket']
            message_match = message_info['ticket']

        elif branch_type == "release":
            branch_match = branch_info['release_version']
            message_match = message_info['release_version']

        if branch_match is None or branch_match != message_match:
            print_c("ERROR", color="light_red")
            print(
                "\nBad branch/message reference\n\n"
                "The reference on the message must\n"
                "match the branch name.\n\n"
                "To have consistent commit messages, it\n"
                "is necessary that the reference used\n"
                "in the commit message is the same as\n"
                "the name used in the branch.\n\n"
                "Change the commit message or use a\n"
                "different branch name.\n"
            )
            return False
        print_c("OK", color='light_green')

    print_c("Check status: ", end='')
    print_c("ALLOWED\n", color="light_green")

    return True


def main():
    print_c("GIT Commit Message Checks\n".center(40), color='white')

    # Read commit message
    with open(sys.argv[1]) as f:
        text = f.read().strip()

    try:
        result = commit_msg(text)
        if not result:
            sys.exit(1)
    except ScriptError as e:
        print_c("Exception raised", color="light_red")
        print(e.message)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

# vim: ft=python:ts=4:sw=4