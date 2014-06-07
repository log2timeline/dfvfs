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
"""The Virtual File System (VFS) path specification key chain object.

The key chain object is used to manage credentials for path specifications.
E.g. BitLocker Drive Encryption (BDE) encrypted volumes can require a
credential (e.g. password) to access the unencrypted data (unlock).
"""

from dfvfs.credentials import manager


class KeyChain(object):
  """Class that implements the VFS key chain."""

  def __init__(self):
    """Initializes the key chain object."""
    super(KeyChain, self).__init__()
    self._credentials_per_path_spec = {}

  def GetCredential(self, path_spec, identifier):
    """Retrieves the credential data from the key chain.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      identifier: string containing the credential identifier.

    Returns:
      The credential data or None if the credential for the path specification
      is not set.
    """
    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    return credentials.get(identifier, None)

  def SetCredential(self, path_spec, identifier, data):
    """Sets a credential in the key chain.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      identifier: string containing the credential identifier.
      data: the credential data.

    Raises:
      KeyError: if the credential is not supported by the path specification
                type.
    """
    supported_credentials = manager.CredentialsManager.GetCredentials(path_spec)

    if identifier not in supported_credentials.CREDENTIALS:
      raise KeyError((
          u'Unsuppored credential: {0:s} for path specification type: '
          u'{1:s}').format(identifier, path_spec.type_indicator))

    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    credentials[identifier] = data
    self._credentials_per_path_spec[path_spec.comparable] = credentials
