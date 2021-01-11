# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file-like object implementation."""

from dfvfs.file_io import data_range_io
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.resolver import resolver


class TSKPartitionFile(data_range_io.DataRange):
  """File input/output (IO) object using pytsk3."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(TSKPartitionFile, self).__init__(resolver_context, path_spec)
    self._file_system = None

  def _Close(self):
    """Closes the file-like object."""
    self._file_system = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)
    tsk_volume = self._file_system.GetTSKVolume()
    tsk_vs, _ = tsk_partition.GetTSKVsPartByPathSpec(
        tsk_volume, self._path_spec)

    if tsk_vs is None:
      raise errors.PathSpecError(
          'Unable to retrieve TSK volume system part from path '
          'specification.')

    range_offset = tsk_partition.TSKVsPartGetStartSector(tsk_vs)
    range_size = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs)

    if range_offset is None or range_size is None:
      raise errors.PathSpecError(
          'Unable to retrieve TSK volume system part data range from path '
          'specification.')

    bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(tsk_volume)
    range_offset *= bytes_per_sector
    range_size *= bytes_per_sector

    self._SetRange(range_offset, range_size)
    self._file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)
