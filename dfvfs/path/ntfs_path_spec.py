# -*- coding: utf-8 -*-
"""The path NTFS specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class NTFSPathSpec(path_spec.PathSpec):
  """Class that implements the NTFS path specification.

  Attributes:
    data_stream: string containing the data stream name, where None indicates
                 the default data stream.
    location: string containing the location.
    mft_attribute: integer containing the $FILE_NAME MFT attribute index. The
                   first attribute is indicated by 0.
    mft_entry: integer containing the MFT entry. The first entry is indicated
               by 0.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def __init__(
      self, data_stream=None, location=None, mft_attribute=None,
      mft_entry=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the NTFS path specification must have a parent.

    Args:
      data_stream: optional string containing the data stream name,
                   where None indicates the default data stream.
      location: optional string containing the location.
      mft_attribute: optional integer containing the $FILE_NAME MFT
                     attribute index. The first attribute is indicated by 0.
      mft_entry: optional integer containing the MFT entry. The first entry
                 is indicated by 0.
      parent: optional parent path specification (instance of PathSpec),
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when location and mft_entry, or parent are not set.
    """
    if (not location and not mft_entry) or not parent:
      raise ValueError(u'Missing location and MFT entry, or parent value.')

    super(NTFSPathSpec, self).__init__(parent=parent, **kwargs)
    self.data_stream = data_stream
    self.location = location
    self.mft_attribute = mft_attribute
    self.mft_entry = mft_entry

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.data_stream:
      string_parts.append(u'data stream: {0:s}'.format(self.data_stream))
    if self.location is not None:
      string_parts.append(u'location: {0:s}'.format(self.location))
    if self.mft_attribute is not None:
      string_parts.append(u'MFT attribute: {0:d}'.format(self.mft_attribute))
    if self.mft_entry is not None:
      string_parts.append(u'MFT entry: {0:d}'.format(self.mft_entry))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(NTFSPathSpec)
