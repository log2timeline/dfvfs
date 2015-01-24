# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file-like object implementation."""

from dfvfs.file_io import data_range_io
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.resolver import resolver


class TSKPartitionFile(data_range_io.DataRange):
  """Class that implements a file-like object using pytsk3."""

  def __init__(self, resolver_context, tsk_volume=None, tsk_vs_part=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      tsk_volume: optional SleuthKit volume object (instance of
                  pytsk3.Volume_Info). The default is None.
      tsk_vs_part: optional SleuthKit file object (instance of
                   pytsk3.TSK_VS_PART_INFO). The default is None.

    Raises:
      ValueError: if tsk_vs_part provided but tsk_volume is not.
    """
    if tsk_vs_part is not None and tsk_volume is None:
      raise ValueError(
          u'TSK volume system part object provided without corresponding '
          u'volume object.')

    super(TSKPartitionFile, self).__init__(resolver_context)
    self._tsk_volume = tsk_volume
    self._tsk_vs = None
    self._tsk_vs_part = tsk_vs_part

    if tsk_vs_part:
      self._tsk_vs_part_set_in_init = True
    else:
      self._tsk_vs_part_set_in_init = False

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      PathSpecError: if the path specification is invalid.
      ValueError: if the path specification is missing.
    """
    if not self._tsk_vs_part_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if not self._tsk_vs_part_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      file_system = resolver.Resolver.OpenFileSystem(
          path_spec, resolver_context=self._resolver_context)
      self._tsk_volume = file_system.GetTSKVolume()
      self._tsk_vs, _ = tsk_partition.GetTSKVsPartByPathSpec(
          self._tsk_volume, path_spec)

      if self._tsk_vs is None:
        raise errors.PathSpecError(
            u'Unable to retrieve TSK volume system part from path '
            u'specification.')

      range_offset = tsk_partition.TSKVsPartGetStartSector(self._tsk_vs)
      range_size = tsk_partition.TSKVsPartGetNumberOfSectors(self._tsk_vs)

      if range_offset is None or range_size is None:
        raise errors.PathSpecError(
            u'Unable to retrieve TSK volume system part data range from path '
            u'specification.')

      bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(
          self._tsk_volume)
      range_offset *= bytes_per_sector
      range_size *= bytes_per_sector

      self.SetRange(range_offset, range_size)
      self._file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)
      self._file_object_set_in_init = True

    super(TSKPartitionFile, self).open(path_spec=path_spec, mode=mode)
