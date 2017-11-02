#!/bin/bash
#
# MIT License
#
# Copyright (c) 2016 Fabrizio Colonna <colofabrix@tin.it>
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
# deploy-register - Autocompletion for the "deploy" script.
# This script must be loaded with: "source deploy-register"
#

##
## Autocomplete function
__deploy_complete() {
    SUPPORT_SCRIPT="support-deploy"
    which "$SUPPORT_SCRIPT" > /dev/null 2>&1 || exit 1

    local list="$(${SUPPORT_SCRIPT} "${COMP_CWORD}" -- "${COMP_WORDS[@]}")"
    local current_word="${COMP_WORDS[COMP_CWORD]}"

    COMPREPLY=($(compgen -W "$list" -- "$current_word"))
}

complete -F __deploy_complete "deploy"

# vim: ft=sh:ts=4:sw=4