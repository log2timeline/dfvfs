#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Virtual File System (VFS) definitions."""

# The compression method definitions.
COMPRESSION_METHOD_BZIP2 = u'bzip2'
COMPRESSION_METHOD_DEFLATE = u'deflate'
COMPRESSION_METHOD_ZLIB = u'zlib'

# The type indicator definitions.
TYPE_INDICATOR_COMPRESSED_STREAM = u'COMPRESSED_STREAM'
TYPE_INDICATOR_DATA_RANGE = u'DATA_RANGE'
TYPE_INDICATOR_EWF = u'EWF'
TYPE_INDICATOR_OS = u'OS'
TYPE_INDICATOR_QCOW = u'QCOW'
TYPE_INDICATOR_TAR = u'TAR'
TYPE_INDICATOR_TSK = u'TSK'
TYPE_INDICATOR_VHDI = u'VHDI'
TYPE_INDICATOR_VSHADOW = u'VSHADOW'
TYPE_INDICATOR_ZIP = u'ZIP'
