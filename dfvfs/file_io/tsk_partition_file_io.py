# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file-like object implementation."""

from dfvfs.file_io import data_range_io
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.resolver import resolver


class TSKPartitionFile(data_range_io.DataRange):
  """Class that implements a file-like object using pytsk3."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(TSKPartitionFile, self).__init__(resolver_context)
    self._file_system = None

  def _Close(self):
    """Closes the file-like object."""
    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specification.')

    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)
    tsk_volume = self._file_system.GetTSKVolume()
    tsk_vs, _ = tsk_partition.GetTSKVsPartByPathSpec(tsk_volume, path_spec)

    if tsk_vs is None:
      raise errors.PathSpecError(
          u'Unable to retrieve TSK volume system part from path '
          u'specification.')

    range_offset = tsk_partition.TSKVsPartGetStartSector(tsk_vs)
    range_size = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs)

    if range_offset is None or range_size is None:
      raise errors.PathSpecError(
          u'Unable to retrieve TSK volume system part data range from path '
          u'specification.')

    bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(tsk_volume)
    range_offset *= bytes_per_sector
    range_size *= bytes_per_sector

    self.SetRange(range_offset, range_size)
    self._file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    self._file_object_set_in_init = True

    # pylint: disable=protected-access
    super(TSKPartitionFile, self)._Open(path_spec=path_spec, mode=mode)
