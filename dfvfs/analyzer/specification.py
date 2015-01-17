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
"""The format specification classes."""


class Signature(object):
  """Class that defines a signature of a format specification.

  The signature consists of a byte string pattern, an optional
  offset relative to the start of the data, and a value to indidate
  if the pattern is bound to the offset.
  """
  def __init__(self, pattern, offset=None):
    """Initializes the signature.

    Args:
      pattern: a binary string containing the pattern of the signature.
               Wildcards or regular pattern (regexp) are not supported.
      offset: the offset of the signature or None by default. None is used
              to indicate the signature has no offset. A positive offset
              is relative from the start of the data a negative offset
              is relative from the end of the data.
    """
    super(Signature, self).__init__()
    self.identifier = None
    self.offset = offset
    self.pattern = pattern

  def SetIdentifier(self, identifier):
    """Sets the identifier of the signature in the specification store.

    Args:
      identifier: a string containing an unique signature identifier for
                  a specification store.
    """
    self.identifier = identifier


class Specification(object):
  """Class that contains a format specification."""

  def __init__(self, identifier):
    """Initializes the specification.

    Args:
      identifier: string containing a unique name for the format.
    """
    self.identifier = identifier
    self.signatures = []

  def AddNewSignature(self, pattern, offset=None):
    """Adds a signature.

    Args:
      pattern: a binary string containing the pattern of the signature.
      offset: the offset of the signature or None by default. None is used
              to indicate the signature has no offset. A positive offset
              is relative from the start of the data a negative offset
              is relative from the end of the data.
    """
    self.signatures.append(Signature(pattern, offset=offset))


class SpecificationStore(object):
  """Class that servers as a store for specifications."""

  def __init__(self):
    """Initializes the specification store."""
    self._format_specifications = {}
    # Maps signature identifiers to format specifications.
    self._signature_map = {}

  @property
  def specifications(self):
    """A specifications iterator object."""
    return self._format_specifications.itervalues()

  def AddNewSpecification(self, identifier):
    """Adds a new specification.

    Args:
      identifier: a string containing the format identifier,
                  which should be unique for the store.

    Returns:
      a instance of Specification.

    Raises:
      KeyError: if the store already contains a specification with
                the same identifier.
    """
    if identifier in self._format_specifications:
      raise KeyError(
          'Specification {0:s} is already defined in store.'.format(identifier))

    self._format_specifications[identifier] = Specification(identifier)

    return self._format_specifications[identifier]

  def AddSpecification(self, specification):
    """Adds a specification.

    Args:
      specification: the specification (instance of Specification).

    Raises:
      KeyError: if the store already contains a specification with
                the same identifier.
    """
    if specification.identifier in self._format_specifications:
      raise KeyError(
          u'Specification {0:s} is already defined in store.'.format(
              specification.identifier))

    self._format_specifications[specification.identifier] = specification

    for signature in specification.signatures:
      signature_index = len(self._signature_map)

      signature_identifier = u'{0:s}:{1:d}'.format(
          specification.identifier, signature_index)

      if signature_identifier in self._signature_map:
        raise KeyError(
            u'Signature {0:s} is already defined in map.'.format(
                signature_identifier))

      signature.SetIdentifier(signature_identifier)
      self._signature_map[signature_identifier] = specification

  def GetSpecificationBySignature(self, signature_identifier):
    """Retrieves a specification mapped to a signature identifier.

    Args:
      identifier: a string containing an unique signature identifier for
                  a specification store.

    Returns:
      A specification (instance of Specification) or None if the signature
      identifier does not exists within the specification store.
    """
    return self._signature_map.get(signature_identifier, None)
