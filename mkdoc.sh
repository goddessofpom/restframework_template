#!/bin/sh
rm -rf apidoc
apidoc -o apidoc/ -f ".*\\.py$" -e "restframework_core/"
