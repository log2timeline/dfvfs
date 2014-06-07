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
"""The BitLocker Drive Encryption (BDE) credentials object."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


# TODO: add means to set the credentials in the bde_volume using the helper?


class BdeCredendials(credentials.Credentials):
  """Class that implements the BDE credentials object."""

  # TODO: add support for key_data credential, needs pybde update.
  CREDENTIALS = frozenset([
      u'password', u'recovery_password', u'startup_key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE


# Register the resolver helpers with the resolver.
manager.CredentialsManager.RegisterCredentials(BdeCredendials())
