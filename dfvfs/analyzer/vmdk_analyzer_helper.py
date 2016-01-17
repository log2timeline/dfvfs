# -*- coding: utf-8 -*-
"""The VMDK format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VMDKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the VMDK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VMDK

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # VMDK descriptor file signature.
    format_specification.AddNewSignature(b'# Disk DescriptorFile', offset=0)

    # VMDK sparse extent file signature.
    format_specification.AddNewSignature(b'KDMV', offset=0)

    # COWD sparse extent file signature.
    format_specification.AddNewSignature(b'COWD', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(VMDKAnalyzerHelper())
