# -*- coding: utf-8 -*-
"""The analyzer helper object interface."""


class AnalyzerHelper(object):
  """Class that implements the analyzer helper object interface."""

  @property
  def format_categories(self):
    """The format categories."""
    format_categories = getattr(self, u'FORMAT_CATEGORIES', None)
    if format_categories is None:
      raise NotImplementedError(
          u'Invalid analyzer helper missing format categories.')
    return format_categories

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, u'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid analyzer helper missing type indicator.')
    return type_indicator

  def AnalyzeFileObject(self, unused_file_object):
    """Retrieves the format specification.

    This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_file_object: a file-like object (instance of file_io.FileIO).

    Returns:
      The type indicator if the file-like object contains a supported format
      or None otherwise.

    Raises:
      RuntimeError: since this is the fall through implementation.
    """
    # Note: not using NotImplementedError here since pylint then will complain
    # derived classes will need to implement the method, which should not
    # be the the case.
    raise RuntimeError(u'Missing implemention to analyze file object.')

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    This is the fall through implementation that returns None.

    Returns:
      The format specification object (instance of FormatSpecification)
      or None if the format cannot be defined by a specification object.
    """
    return

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      A boolean value to indicate the analyzer helper is enabled.
    """
    return True
