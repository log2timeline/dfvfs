# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class TSKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """TSK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # FAT volume header signature.
    format_specification.AddNewSignature(b'\x55\xaa', offset=510)

    if definitions.PREFERRED_NTFS_BACK_END == self.TYPE_INDICATOR:
      # NTFS file system signature.
      format_specification.AddNewSignature(b'NTFS    ', offset=3)

    # HFS boot block signature.
    format_specification.AddNewSignature(b'LK', offset=0)

    # HFS master directory block signature.
    format_specification.AddNewSignature(b'BD', offset=0)

    if definitions.PREFERRED_HFS_BACK_END == self.TYPE_INDICATOR:
      # HFS+ file system signature.
      format_specification.AddNewSignature(b'H+', offset=1024)

      # HFSX file system signature.
      format_specification.AddNewSignature(b'HX', offset=1024)

    if definitions.PREFERRED_EXT_BACK_END == self.TYPE_INDICATOR:
      # Ext file system signature.
      format_specification.AddNewSignature(b'\x53\xef', offset=1080)

    # ISO9660 file system signature.
    format_specification.AddNewSignature(b'CD001', offset=32769)

    # YAFFS file system signature.

    return format_specification


analyzer.Analyzer.RegisterHelper(TSKAnalyzerHelper())
