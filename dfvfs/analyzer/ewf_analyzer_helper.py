# -*- coding: utf-8 -*-
"""The EWF format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class EWFAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """EWF analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE,
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EWF

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # EWF version 1 signature and start of fields.
    format_specification.AddNewSignature(
        b'EVF\x09\x0d\x0a\xff\x00\x01', offset=0)

    # EWF version 2 signature and major version.
    format_specification.AddNewSignature(b'EVF2\r\n\x81\x00\x02', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(EWFAnalyzerHelper())
