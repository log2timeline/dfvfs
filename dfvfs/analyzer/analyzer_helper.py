# -*- coding: utf-8 -*-
"""The analyzer helper interface."""

from __future__ import unicode_literals

from dfvfs.lib import errors


class AnalyzerHelper(object):
  """Analyzer helper interface."""

  # pylint: disable=redundant-returns-doc

  def __init__(self):
    """Initializes an analyzer helper.

    Raises:
      ValueError: if a derived analyzer helper class does not define format
          categories or a type indicator.
    """
    super(AnalyzerHelper, self).__init__()

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

    if not getattr(self, 'FORMAT_CATEGORIES', None):
      raise ValueError('Missing format categories.')

  @property
  def format_categories(self):
    """set[str]: format categories, such as archive file or file system.

    The format categories are defined in definitions.FORMAT_CATEGORIES.
    """
    # pylint: disable=no-member
    return self.FORMAT_CATEGORIES

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR

  def AnalyzeFileObject(self, unused_file_object):
    """Retrieves the format specification.

    This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_file_object (FileIO): file-like object.

    Returns:
      str: type indicator if the file-like object contains a supported format
          or None otherwise.

    Raises:
      NotSupported: since this is the fall through implementation.
    """
    raise errors.NotSupported(
        'Missing implementation to analyze file-like object.')

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    This is the fall through implementation that returns None.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    return None

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return True
