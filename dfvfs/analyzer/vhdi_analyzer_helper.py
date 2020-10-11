# -*- coding: utf-8 -*-
"""The Virtual Hard Disk image (VHDI) format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VHDIAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Virtual Hard Disk image (VHDI) analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # Virtual Hard Disk version 1 (VHD) signature in footer.
    format_specification.AddNewSignature(b'conectix', offset=-512)

    # Virtual Hard Disk version 2 (VHDX) signature in file information.
    format_specification.AddNewSignature(b'vhdxfile', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(VHDIAnalyzerHelper())
