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
"""The EWF image file-like object."""

import pyewf

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.path import factory as path_spec_factory


if pyewf.get_version() < '20131210':
  raise ImportWarning('EwfFile requires at least pyewf 20131210.')


class EwfFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyewf."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object.

    Raises:
      PathSpecError: if the path specification is invalid.
      RuntimeError: if the maximum number of supported segment files is
                    reached.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    parent_path_spec = path_spec.parent

    parent_location = getattr(parent_path_spec, 'location', None)
    if not parent_location:
      raise errors.PathSpecError(
          u'Unsupported parent path specification without location.')

    # Note that we cannot use pyewf's glob function since it does not
    # handle the file system abstraction dfvfs provides.

    file_system = resolver.Resolver.OpenFileSystem(
        parent_path_spec, resolver_context=self._resolver_context)

    parent_location, _, segment_extension = parent_location.rpartition(u'.')
    segment_extension_length = len(segment_extension)

    if (segment_extension_length not in [3, 4] or
        not segment_extension.endswith(u'01') or (
            segment_extension_length == 3 and
            segment_extension[0] not in ['E', 'e', 's']) or (
            segment_extension_length == 4 and
            not segment_extension.starstwith(u'Ex'))):
      raise errors.PathSpecError(
          u'Unsupported parent path specification invalid segment file '
          u'extenstion.')

    segment_number = 1
    segment_files = []
    while True:
      segment_location = u'{0:s}.{1:s}'.format(
          parent_location, segment_extension)

      # Note that we don't want to set the keyword arguments when not used
      # because the path specification base class will check for unused
      # keyword arguments and raise.
      kwargs = path_spec_factory.Factory.GetProperties(parent_path_spec)

      kwargs['location'] = segment_location
      if parent_path_spec.parent is not None:
        kwargs['parent'] = parent_path_spec.parent

      segment_path_spec = path_spec_factory.Factory.NewPathSpec(
        parent_path_spec.type_indicator, **kwargs)

      if not file_system.FileEntryExistsByPathSpec(segment_path_spec):
        break

      segment_files.append(segment_path_spec)

      segment_number += 1
      if segment_number <= 99:
        if segment_extension_length == 3:
          segment_extension = u'{0:s}{1:02d}'.format(
              segment_extension[0], segment_number)
        elif segment_extension_length == 4:
          segment_extension = u'{0:s}x{1:02d}'.format(
              segment_extension[0], segment_number)

      else:
        segment_index = segment_number - 100

        quotient, remainder = divmod(segment_index, 26)

        if quotient > 26:
          raise RuntimeError(u'Unsupported number of segment files.')

        first_letter = segment_extension[0]

        if segment_extension[0] in ['e', 's']:
          letter_offset = ord('a')
        else:
          letter_offset = ord('A')

        # The quotient is used to calculate the second letter
        # while the remainder indicates the third and last.
        second_letter = chr(letter_offset + quotient)
        third_letter = chr(letter_offset + remainder)

        if segment_extension_length == 3:
          segment_extension = u'{0:s}{1:s}{2:s}'.format(
              first_letter, second_letter, third_letter)
        elif segment_extension_length == 4:
          segment_extension = u'{0:s}x{1:s}{2:s}'.format(
              first_letter, second_letter, third_letter)

    if not segment_files:
      return None

    file_objects = []
    for segment_path_spec in segment_files:
      file_object = resolver.Resolver.OpenFileObject(
          segment_path_spec, resolver_context=self._resolver_context)
      file_objects.append(file_object)

    ewf = pyewf.handle()
    ewf.open_file_objects(file_objects)
    return ewf

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
