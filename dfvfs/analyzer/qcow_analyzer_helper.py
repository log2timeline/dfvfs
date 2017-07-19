# -*- coding: utf-8 -*-
"""The QCOW format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class QCOWAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """QCOW analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_QCOW

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # QCOW version 1 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x01', offset=0)

    # QCOW version 2 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x02', offset=0)

    # QCOW version 3 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x03', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(QCOWAnalyzerHelper())
