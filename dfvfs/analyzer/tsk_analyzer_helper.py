# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) format analyzer helper implementation."""

import pytsk3

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions
from dfvfs.lib import tsk_image


class TSKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the TSK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def AnalyzeFileObject(self, file_object):
    """Retrieves the format specification.

    Args:
      file_object: a file-like object (instance of file_io.FileIO).

    Returns:
      The type indicator if the file-like object contains a supported format
      or None otherwise.
    """
    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)

    try:
      _ = pytsk3.FS_Info(tsk_image_object)
    except IOError:
      return

    return self.type_indicator


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(TSKAnalyzerHelper())
