#!/bin/bash

#
# Bash script test 00:
# Search for “my konfu is the best” in all *.py files, print matched file list
#

find -type f -name '*.py' -exec grep 'my konfu is the best' /dev/null {} \;

