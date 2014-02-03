#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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

from dfvfs.resolver import compressed_stream_resolver_helper
from dfvfs.resolver import data_range_resolver_helper

try:
  from dfvfs.resolver import ewf_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import fake_resolver_helper
from dfvfs.resolver import gzip_resolver_helper
from dfvfs.resolver import os_resolver_helper

try:
  from dfvfs.resolver import qcow_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import tar_resolver_helper

try:
  from dfvfs.resolver import tsk_partition_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import tsk_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import vhdi_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import vshadow_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import zip_resolver_helper
