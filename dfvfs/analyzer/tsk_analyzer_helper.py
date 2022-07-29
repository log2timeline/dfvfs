# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) format analyzer helper implementation."""

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

    if definitions.PREFERRED_FAT_BACK_END == self.TYPE_INDICATOR:
      # Boot sector signature.
      format_specification.AddNewSignature(b'\x55\xaa', offset=510)

      # FAT-12 and FAT-16 file system hint.
      format_specification.AddNewSignature(b'FAT12   ', offset=54)
      format_specification.AddNewSignature(b'FAT16   ', offset=54)

      # FAT-32 file system hint.
      format_specification.AddNewSignature(b'FAT32   ', offset=82)

      # exFAT file system signature.
      format_specification.AddNewSignature(b'EXFAT   ', offset=3)

    if definitions.PREFERRED_NTFS_BACK_END == self.TYPE_INDICATOR:
      # NTFS file system signature.
      format_specification.AddNewSignature(b'NTFS    ', offset=3)

    if definitions.PREFERRED_HFS_BACK_END == self.TYPE_INDICATOR:
      # HFS boot block signature.
      # format_specification.AddNewSignature(b'LK', offset=0)

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
