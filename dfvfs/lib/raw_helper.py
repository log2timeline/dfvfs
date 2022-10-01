# -*- coding: utf-8 -*-
"""Helper functions for RAW storage media image support."""

from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory


def _RawGlobPathSpecWithAlphabeticalSchema(
    file_system, parent_path_spec, segment_format, location, segment_length,
    upper_case=False):
  """Globs for path specifications according to an alphabetical naming schema.

  Args:
    file_system (FileSystem): file system.
    parent_path_spec (PathSpec): parent path specification.
    segment_format (str): naming schema of the segment file location.
    location (str): the base segment file location string.
    segment_length (int): length (number of characters) of the segment
        indicator.
    upper_case (Optional[bool]): True if the segment name is in upper case.

  Returns:
    list[PathSpec]: path specifications that match the glob.
  """
  segment_number = 0
  segment_files = []

  while True:
    segment_index = segment_number
    segment_letters = []
    while len(segment_letters) < segment_length:
      segment_index, remainder = divmod(segment_index, 26)
      if upper_case:
        segment_letters.append(chr(ord('A') + remainder))
      else:
        segment_letters.append(chr(ord('a') + remainder))

    # Reverse the segment letters list to form the extension.
    segment_letters = ''.join(segment_letters[::-1])
    segment_location = segment_format.format(location, segment_letters)

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

  return segment_files


def _RawGlobPathSpecWithNumericSchema(
    file_system, parent_path_spec, segment_format, location, segment_number):
  """Globs for path specifications according to a numeric naming schema.

  Args:
    file_system (FileSystem): file system.
    parent_path_spec (PathSpec): parent path specification.
    segment_format (str): naming schema of the segment file location.
    location (str): the base segment file location string.
    segment_number (int): first segment number.

  Returns:
    list[PathSpec]: path specifications that match the glob.
  """
  segment_files = []

  while True:
    segment_location = segment_format.format(location, segment_number)

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

  return segment_files


def RawGlobPathSpec(file_system, path_spec):
  """Globs for path specifications according to the split RAW naming schema.

  Args:
    file_system (FileSystem): file system.
    path_spec (PathSpec): path specification.

  Returns:
    list[PathSpec]: path specifications that match the glob.

  Raises:
    PathSpecError: if the path specification is invalid.
    RuntimeError: if the maximum number of supported segment files is
        reached.
  """
  if not path_spec.HasParent():
    raise errors.PathSpecError(
        'Unsupported path specification without parent.')

  parent_path_spec = path_spec.parent

  parent_location = getattr(parent_path_spec, 'location', None)
  if not parent_location:
    raise errors.PathSpecError(
        'Unsupported parent path specification without location.')

  path_segments = file_system.SplitPath(parent_location)
  last_path_segment = path_segments.pop()
  filename_prefix, dot, segment_extension = last_path_segment.rpartition('.')

  if not dot:
    filename_prefix = segment_extension
    segment_extension = ''

  segment_extension_length = len(segment_extension)

  path_segments.append(filename_prefix)
  location = file_system.JoinPath(path_segments)

  if not segment_extension:
    filename_prefix_length = len(filename_prefix)

    # Check if there are muliple segment files in the form: PREFIX[a-z]+
    # where [a-z]+ starts with a and consist of multiple letters,
    # e.g. PREFIXaa or PREFIXzz.
    if filename_prefix[-2:] == 'aa':
      suffix_index = filename_prefix_length - 4
      while suffix_index >= 0:
        if filename_prefix[suffix_index] != 'a':
          suffix_index += 1
          break
        suffix_index -= 1

      suffix_length = filename_prefix_length - suffix_index
      segment_files = _RawGlobPathSpecWithAlphabeticalSchema(
          file_system, parent_path_spec, '{0:s}{1:s}',
          location[:-suffix_length], filename_prefix_length - suffix_index,
          upper_case=False)

    # Check if there are muliple segment files in the form: PREFIX[A-Z]+
    # where [A-Z]+ starts with A and consist of multiple letters,
    # e.g. PREFIXAA or PREFIXZZ.
    elif filename_prefix[-2:] == 'AA':
      suffix_index = filename_prefix_length - 4
      while suffix_index >= 0:
        if filename_prefix[suffix_index] != 'A':
          suffix_index += 1
          break
        suffix_index -= 1

      suffix_length = filename_prefix_length - suffix_index
      segment_files = _RawGlobPathSpecWithAlphabeticalSchema(
          file_system, parent_path_spec, '{0:s}{1:s}',
          location[:-suffix_length], filename_prefix_length - suffix_index,
          upper_case=True)

    # Check if there are muliple segment files in the form: PREFIX#
    # where # starts with either 0 or 1 and consist of multiple digits,
    # e.g. PREFIX1 or PREFIX000.
    elif filename_prefix[-1].isdigit():
      suffix_index = filename_prefix_length - 2
      while suffix_index >= 0:
        if not filename_prefix[suffix_index].isdigit():
          suffix_index += 1
          break
        suffix_index -= 1

      try:
        segment_number = int(filename_prefix[suffix_index:], 10)
      except ValueError:
        raise errors.PathSpecError(
            'Unsupported path specification invalid segment file scheme.')

      if segment_number not in [0, 1]:
        raise errors.PathSpecError(
            'Unsupported path specification invalid segment file scheme.')

      suffix_length = filename_prefix_length - suffix_index
      if suffix_length == 1:
        segment_format = '{0:s}{1:d}'
      elif suffix_length == 2:
        segment_format = '{0:s}{1:02d}'
      elif suffix_length == 3:
        segment_format = '{0:s}{1:03d}'
      elif suffix_length == 4:
        segment_format = '{0:s}{1:04d}'
      else:
        raise errors.PathSpecError(
            'Unsupported path specification invalid segment file scheme.')

      segment_files = _RawGlobPathSpecWithNumericSchema(
          file_system, parent_path_spec, segment_format,
          location[:-suffix_length], segment_number)
    else:
      segment_files = []

  # Check if there is single segment file e.g. PREFIX.dd, PREFIX.dmg,
  # PREFIX.img, PREFIX.raw.
  elif segment_extension.lower() in ['dd', 'dmg', 'img', 'raw']:
    if file_system.FileEntryExistsByPathSpec(parent_path_spec):
      segment_files = [parent_path_spec]
    else:
      segment_files = []

  # Check if there are muliple segment files in the form: PREFIX.[a-z]+
  # where [a-z]+ starts with a and consist of multiple letters,
  # e.g. PREFIX.aa or PREFIX.aaa.
  elif segment_extension == 'a' * segment_extension_length:
    segment_files = _RawGlobPathSpecWithAlphabeticalSchema(
        file_system, parent_path_spec, '{0:s}.{1:s}', location,
        segment_extension_length, upper_case=False)

  # Check if there are muliple segment files in the form: PREFIX.[A-Z]+
  # where [A-Z]+ starts with A and consist of multiple letters,
  # e.g. PREFIX.AA or PREFIX.AAA.
  elif segment_extension == 'A' * segment_extension_length:
    segment_files = _RawGlobPathSpecWithAlphabeticalSchema(
        file_system, parent_path_spec, '{0:s}.{1:s}', location,
        segment_extension_length, upper_case=True)

  # Check if there are muliple segment files in the form: PREFIX###.asb
  # where # starts with 1 and consist of multiple digits e.g. PREFIX001.asb.
  elif segment_extension == 'asb':
    if location[-3:] == '001':
      segment_files = _RawGlobPathSpecWithNumericSchema(
          file_system, parent_path_spec, '{0:s}{1:03d}.asb', location[:-3], 1)
    else:
      segment_files = []

  # Check if there are muliple segment files in the form: PREFIX-f###.vmdk
  # where # starts with 1 and consist of multiple digits,
  # e.g. PREFIX-f001.vmdk.
  elif segment_extension == 'vmdk':
    location, _, segment_number = location.partition('-f')
    if segment_number == '001':
      segment_files = _RawGlobPathSpecWithNumericSchema(
          file_system, parent_path_spec, '{0:s}-f{1:03d}.vmdk', location, 1)
    else:
      segment_files = []

  # Check if there are muliple segment files in the form: PREFIX.#
  # where # starts with either 0 or 1 and consist of multiple digits,
  # e.g. PREFIX.1 or PREFIX.000.
  elif segment_extension.isdigit():
    try:
      segment_number = int(segment_extension, 10)
    except ValueError:
      raise errors.PathSpecError((
          f'Unsupported path specification invalid segment file extension: '
          f'{segment_extension:s}'))

    if segment_number not in [0, 1]:
      raise errors.PathSpecError((
          f'Unsupported path specification invalid segment file extension: '
          f'{segment_extension:s}'))

    if segment_extension_length == 1:
      segment_format = '{0:s}.{1:d}'
    elif segment_extension_length == 2:
      segment_format = '{0:s}.{1:02d}'
    elif segment_extension_length == 3:
      segment_format = '{0:s}.{1:03d}'
    elif segment_extension_length == 4:
      segment_format = '{0:s}.{1:04d}'
    else:
      raise errors.PathSpecError((
          f'Unsupported path specification invalid segment file extension: '
          f'{segment_extension:s}'))

    segment_files = _RawGlobPathSpecWithNumericSchema(
        file_system, parent_path_spec, segment_format, location, segment_number)

  else:
    segment_files = []

    # Check if there are muliple segment files in the form: PREFIX.#of#
    # e.g. PREFIX.1of5 - PREFIX.5of5.
    segment_number, _, number_of_segments = segment_extension.partition('of')

    if segment_number.isdigit() and number_of_segments.isdigit():
      try:
        segment_number = int(segment_number, 10)
        number_of_segments = int(number_of_segments, 10)
      except ValueError:
        raise errors.PathSpecError((
            f'Unsupported path specification invalid segment file extension: '
            f'{segment_extension:s}'))

      if segment_number != 1:
        raise errors.PathSpecError((
            f'Unsupported path specification invalid segment file extension: '
            f'{segment_extension:s}'))

      for segment_number in range(1, number_of_segments + 1):
        segment_location = (
            f'{location:s}.{segment_number:d}of{number_of_segments:d}')

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
          raise errors.PathSpecError((
              f'Missing segment file: {segment_number:d}of'
              f'{number_of_segments:d} for extension: {segment_extension:s}'))

      segment_files.append(segment_path_spec)

  return segment_files
