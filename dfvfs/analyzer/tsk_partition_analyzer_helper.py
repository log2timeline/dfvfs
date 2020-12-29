# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition format analyzer helper implementation."""

import pytsk3

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions
from dfvfs.lib import tsk_image


class TSKPartitionAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """TSK partition analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def AnalyzeFileObject(self, file_object):
    """Retrieves the format specification.

    Args:
      file_object (FileIO): file-like object.

    Returns:
      str: type indicator if the file-like object contains a supported format
          or None otherwise.
    """
    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)

    try:
      pytsk3.Volume_Info(tsk_image_object)
    except IOError:
      return None

    return self.type_indicator


analyzer.Analyzer.RegisterHelper(TSKPartitionAnalyzerHelper())
