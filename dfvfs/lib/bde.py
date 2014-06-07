#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""Helper function for the BitLocker Drive Encryption (BDE) support."""


def BdeVolumeOpen(bde_volume, path_spec, file_object):
  """Opens the BDE volume using the path specification.

  Args:
    bde_volume: the BDE volume (instance of pybde.volume).
    path_spec: the path specification (instance of path.PathSpec).
    file_object: the file-like object (instance of FileIO).
  """
  password = getattr(path_spec, u'password', None)
  if password:
    bde_volume.set_password(password)

  recovery_password = getattr(path_spec, u'recovery_password', None)
  if recovery_password:
    bde_volume.set_recovery_password(recovery_password)

  startup_key = getattr(path_spec, u'startup_key', None)
  if startup_key:
    bde_volume.read_startup_key(startup_key)

  bde_volume.open_file_object(file_object)
