# -*- coding: utf-8 -*-
"""The VMDK format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VMDKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """VMDK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VMDK

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # VMDK descriptor file signature.
    format_specification.AddNewSignature(b'# Disk DescriptorFile', offset=0)

    # VMDK sparse extent file signature.
    format_specification.AddNewSignature(b'KDMV', offset=0)

    # COWD sparse extent file signature.
    format_specification.AddNewSignature(b'COWD', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(VMDKAnalyzerHelper())
