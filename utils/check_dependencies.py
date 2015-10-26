#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to check for the availability and version of dependencies."""

from __future__ import print_function
import sys

# Change PYTHONPATH to include dfVFS.
sys.path.insert(0, u'.')

import dfvfs.dependencies


if __name__ == u'__main__':
  if not dfvfs.dependencies.CheckDependencies(latest_version_check=True):
    build_instructions_url = (
        u'https://github.com/log2timeline/dfvfs/wiki/Building')

    print(u'See: {0:s} on how to set up dfVFS.'.format(build_instructions_url))
    print(u'')
