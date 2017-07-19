# -*- coding: utf-8 -*-
"""The analyzer helper interface."""

from __future__ import unicode_literals


class AnalyzerHelper(object):
  """Analyzer helper interface."""

  @property
  def format_categories(self):
    """The format categories."""
    format_categories = getattr(self, 'FORMAT_CATEGORIES', None)
    if format_categories is None:
      raise NotImplementedError(
          'Invalid analyzer helper missing format categories.')
    return format_categories

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          'Invalid analyzer helper missing type indicator.')
    return type_indicator

  def AnalyzeFileObject(self, unused_file_object):
    """Retrieves the format specification.

    This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_file_object (FileIO): file-like object.

    Returns:
      str: type indicator if the file-like object contains a supported format
          or None otherwise.

    Raises:
      RuntimeError: since this is the fall through implementation.
    """
    # Note: not using NotImplementedError here since pylint then will complain
    # derived classes will need to implement the method, which should not
    # be the the case.
    raise RuntimeError('Missing implemention to analyze file object.')

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    This is the fall through implementation that returns None.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    return

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return True
