# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class GPTAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """GPT analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # GPT signature.
    format_specification.AddNewSignature(b'EFI PART', offset=512)
    format_specification.AddNewSignature(b'EFI PART', offset=1024)
    format_specification.AddNewSignature(b'EFI PART', offset=2048)
    format_specification.AddNewSignature(b'EFI PART', offset=4096)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return definitions.PREFERRED_GPT_BACK_END == self.TYPE_INDICATOR


analyzer.Analyzer.RegisterHelper(GPTAnalyzerHelper())
