# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class TSKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the TSK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
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

    # HFS+ file system signature.
    format_specification.AddNewSignature(b'H+', offset=1024)

    # HFSX file system signature.
    format_specification.AddNewSignature(b'HX', offset=1024)

    # Ext file system signature.
    format_specification.AddNewSignature(b'\x53\xef', offset=1080)

    # ISO9660 file system signature.
    format_specification.AddNewSignature(b'CD001', offset=32769)

    # YAFFS file system signature.

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(TSKAnalyzerHelper())
