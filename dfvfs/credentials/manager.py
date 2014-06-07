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
"""The Virtual File System (VFS) path specification credentials manager object.

The credentials manager uses credential (instances of Credentials) to specify
which credentials a specific path specification type supports. E.g. in case
of  BitLocker Drive Encryption (BDE):
  * password;
  * recovery password;
  * startup key;
  * key data.
"""


class CredentialsManager(object):
  """Class that implements the credentials manager."""

  _credentials = {}

  @classmethod
  def DeregisterCredentials(cls, credentials):
    """Deregisters a path specification credentials.

    Args:
      credentials: the credentials object (instance of credentials.Credentials).

    Raises:
      KeyError: if credential object is not set for the corresponding
                type indicator.
    """
    if credentials.type_indicator not in cls._credentials:
      raise KeyError(
          u'Credential object not set for type indicator: {0:s}.'.format(
              credentials.type_indicator))

    del cls._credentials[credentials.type_indicator]

  @classmethod
  def GetCredentials(cls, path_spec):
    """Retrieves the credentials for a specific path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The credentials (instance of credentials.Credentials) or None if the path
      specification has no credentials support.
    """
    return cls._credentials.get(path_spec.type_indicator, None)

  @classmethod
  def RegisterCredentials(cls, credentials):
    """Registers a path specification credentials.

    Args:
      credentials: the credentials object (instance of credentials.Credentials).

    Raises:
      KeyError: if credentials object is already set for the corresponding
                type indicator.
    """
    if credentials.type_indicator in cls._credentials:
      raise KeyError(
          u'Credentials object already set for type indicator: {0:s}.'.format(
              credentials.type_indicator))

    cls._credentials[credentials.type_indicator] = credentials
