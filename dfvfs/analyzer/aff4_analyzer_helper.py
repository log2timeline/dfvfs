# -*- coding: utf-8 -*-
"""The AFF4 format analyzer helper implementation."""

import zipfile

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions


class AFF4AnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """AFF4 analyzer helper."""

  _INFORMATION_TURTLE = 'information.turtle'

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_AFF4

  def AnalyzeFileObject(self, file_object):
    """Determines if the file-like object contains a physical AFF4 image.

    Args:
      file_object (FileIO): file-like object.

    Returns:
      str: type indicator if the file-like object contains a supported format
          or None otherwise.
    """
    try:
      file_object.seek(0, 0)
      with zipfile.ZipFile(file_object, 'r') as zip_file:
        if self._INFORMATION_TURTLE not in zip_file.namelist():
          return None

        metadata = zip_file.read(self._INFORMATION_TURTLE)
    except (KeyError, OSError, zipfile.BadZipFile):
      return None

    has_disk_image = (
        b'aff4:DiskImage' in metadata or b'aff4:ContiguousImage' in metadata)
    has_data_stream = b'aff4:dataStream' in metadata

    if has_disk_image and has_data_stream:
      return self.type_indicator

    return None


analyzer.Analyzer.RegisterHelper(AFF4AnalyzerHelper())
