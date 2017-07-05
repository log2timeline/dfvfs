# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class LVMAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """LVM analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # LVM signature.
    format_specification.AddNewSignature(b'LABELONE', offset=0)
    format_specification.AddNewSignature(b'LABELONE', offset=512)
    format_specification.AddNewSignature(b'LABELONE', offset=1024)
    format_specification.AddNewSignature(b'LABELONE', offset=1536)

    return format_specification


analyzer.Analyzer.RegisterHelper(LVMAnalyzerHelper())
