# -*- coding: utf-8 -*-
"""Helper functions for EWF image support."""

from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory


def EWFGlobPathSpec(file_system, path_spec):
  """Globs for path specifications according to the EWF naming schema.

  Args:
    file_system: the file system object (instance of FileSystem).
    path_spec: the path specification (instance of PathSpec).

  Returns:
    A list of the path specifications that match the glob.

  Raises:
    PathSpecError: if the path specification is invalid.
    RuntimeError: if the maximum number of supported segment files is
                  reached.
  """
  if not path_spec.HasParent():
    raise errors.PathSpecError(
        u'Unsupported path specification without parent.')

  parent_path_spec = path_spec.parent

  parent_location = getattr(parent_path_spec, u'location', None)
  if not parent_location:
    raise errors.PathSpecError(
        u'Unsupported parent path specification without location.')

  parent_location, _, segment_extension = parent_location.rpartition(u'.')
  segment_extension_start = segment_extension[0]
  segment_extension_length = len(segment_extension)

  if (segment_extension_length not in [3, 4] or
      not segment_extension.endswith(u'01') or (
          segment_extension_length == 3 and
          segment_extension_start not in [u'E', u'e', u's']) or (
              segment_extension_length == 4 and
              not segment_extension.startswith(u'Ex'))):
    raise errors.PathSpecError((
        u'Unsupported parent path specification invalid segment file '
        u'extension: {0:s}').format(segment_extension))

  segment_number = 1
  segment_files = []
  while True:
    segment_location = u'{0:s}.{1:s}'.format(parent_location, segment_extension)

    # Note that we don't want to set the keyword arguments when not used
    # because the path specification base class will check for unused
    # keyword arguments and raise.
    kwargs = path_spec_factory.Factory.GetProperties(parent_path_spec)

    kwargs[u'location'] = segment_location
    if parent_path_spec.parent is not None:
      kwargs[u'parent'] = parent_path_spec.parent

    segment_path_spec = path_spec_factory.Factory.NewPathSpec(
        parent_path_spec.type_indicator, **kwargs)

    if not file_system.FileEntryExistsByPathSpec(segment_path_spec):
      break

    segment_files.append(segment_path_spec)

    segment_number += 1
    if segment_number <= 99:
      if segment_extension_length == 3:
        segment_extension = u'{0:s}{1:02d}'.format(
            segment_extension_start, segment_number)
      elif segment_extension_length == 4:
        segment_extension = u'{0:s}x{1:02d}'.format(
            segment_extension_start, segment_number)

    else:
      segment_index = segment_number - 100

      if segment_extension_start in [u'e', u's']:
        letter_offset = ord(u'a')
      else:
        letter_offset = ord(u'A')

      segment_index, remainder = divmod(segment_index, 26)
      third_letter = chr(letter_offset + remainder)

      segment_index, remainder = divmod(segment_index, 26)
      second_letter = chr(letter_offset + remainder)

      first_letter = chr(ord(segment_extension_start) + segment_index)
      if first_letter in [u'[', u'{']:
        raise RuntimeError(u'Unsupported number of segment files.')

      if segment_extension_length == 3:
        segment_extension = u'{0:s}{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)
      elif segment_extension_length == 4:
        segment_extension = u'{0:s}x{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

  return segment_files
