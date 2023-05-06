# -*- coding: utf-8 -*-
"""The Apple Partition Map (APM) format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class APMAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """APM analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APM

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # APM signature.
    # Note that technically "PM" at offset 512 is the Apple Partion Map
    # signature but using the partition type is less error prone.
    format_specification.AddNewSignature((
        b'Apple_partition_map\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00'), offset=560)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return definitions.PREFERRED_APM_BACK_END == self.TYPE_INDICATOR


analyzer.Analyzer.RegisterHelper(APMAnalyzerHelper())
