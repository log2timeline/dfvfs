# -*- coding: utf-8 -*-
"""The path NTFS specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class NTFSPathSpec(path_spec.PathSpec):
  """NTFS path specification.

  Attributes:
    data_stream (str): data stream name, where None indicates the default
        data stream.
    location (str): location.
    mft_attribute (int): $FILE_NAME MFT attribute index, where the first
        attribute is indicated by 0.
    mft_entry (int): MFT entry, where the first entry is indicated by 0.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def __init__(
      self, data_stream=None, location=None, mft_attribute=None,
      mft_entry=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the NTFS path specification must have a parent.

    Args:
      data_stream (Optional[str]): data stream name, where None indicates
          the default data stream.
      location (Optional[str]): location.
      mft_attribute (Optional[int]): $FILE_NAME MFT attribute index, where
          the first attribute is indicated by 0.
      mft_entry (Optional[int]): MFT entry, where the first entry is indicated
          by 0.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when location and mft_entry, or parent are not set.
    """
    if (not location and mft_entry is None) or not parent:
      raise ValueError('Missing location and MFT entry, or parent value.')

    super(NTFSPathSpec, self).__init__(parent=parent, **kwargs)
    self.data_stream = data_stream
    self.location = location
    self.mft_attribute = mft_attribute
    self.mft_entry = mft_entry

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.data_stream:
      string_parts.append('data stream: {0:s}'.format(self.data_stream))
    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))
    if self.mft_attribute is not None:
      string_parts.append('MFT attribute: {0:d}'.format(self.mft_attribute))
    if self.mft_entry is not None:
      string_parts.append('MFT entry: {0:d}'.format(self.mft_entry))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(NTFSPathSpec)
