# -*- coding: utf-8 -*-
"""The BDE format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class BDEAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the BDE analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # BDE signature.
    format_specification.AddNewSignature(b'-FVE-FS-', offset=3)

    # BDE ToGo BDE identifier.
    format_specification.AddNewSignature(
        b'\x3b\xd6\x67\x49\x29\x2e\xd8\x4a\x83\x99\xf6\xa3\x39\xe3\xd0\x01',
        offset=424)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(BDEAnalyzerHelper())
