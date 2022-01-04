# -*- coding: utf-8 -*-
"""Helper functions for SleuthKit (TSK) partition support."""

import pytsk3


def GetTSKVsPartByPathSpec(tsk_volume, path_spec):
  """Retrieves the TSK volume system part object from the TSK volume object.

  Args:
    tsk_volume (pytsk3.Volume_Info): TSK volume information.
    path_spec (PathSpec): path specification.

  Returns:
    tuple: containing:

      pytsk3.TSK_VS_PART_INFO: TSK volume system part information or
          None on error.
      int: partition index or None if not available.
  """
  location = getattr(path_spec, 'location', None)
  part_index = getattr(path_spec, 'part_index', None)
  start_offset = getattr(path_spec, 'start_offset', None)
  partition_index = None

  if part_index is None:
    if location is not None:
      if location.startswith('/p'):
        try:
          partition_index = int(location[2:], 10) - 1
        except ValueError:
          pass

      if partition_index is None or partition_index < 0:
        location = None

    if location is None and start_offset is None:
      return None, None

  bytes_per_sector = TSKVolumeGetBytesPerSector(tsk_volume)
  current_part_index = 0
  current_partition_index = 0
  tsk_vs_part = None

  # pytsk3 does not handle the Volume_Info iterator correctly therefore
  # the explicit cast to list is needed to prevent the iterator terminating
  # too soon or looping forever.
  tsk_vs_part_list = list(tsk_volume)
  number_of_tsk_vs_parts = len(tsk_vs_part_list)

  if number_of_tsk_vs_parts > 0:
    if (part_index is not None and
        (part_index < 0 or part_index >= number_of_tsk_vs_parts)):
      return None, None

    for tsk_vs_part in tsk_vs_part_list:
      if TSKVsPartIsAllocated(tsk_vs_part):
        if partition_index is not None:
          if partition_index == current_partition_index:
            break
        current_partition_index += 1

      if part_index is not None and part_index == current_part_index:
        break

      if start_offset is not None:
        start_sector = TSKVsPartGetStartSector(tsk_vs_part)

        if start_sector is not None:
          start_sector *= bytes_per_sector
          if start_sector == start_offset:
            break

      current_part_index += 1

  # Note that here we cannot solely rely on testing if tsk_vs_part is set
  # since the for loop will exit with tsk_vs_part set.
  if tsk_vs_part is None or current_part_index >= number_of_tsk_vs_parts:
    return None, None

  if not TSKVsPartIsAllocated(tsk_vs_part):
    current_partition_index = None
  return tsk_vs_part, current_partition_index


def TSKVolumeGetBytesPerSector(tsk_volume):
  """Retrieves the number of bytes per sector from a TSK volume object.

  Args:
    tsk_volume (pytsk3.Volume_Info): TSK volume information.

  Returns:
    int: number of bytes per sector or 512 by default.
  """
  # Note that because pytsk3.Volume_Info does not explicitly defines info
  # we need to check if the attribute exists and has a value other
  # than None. Default to 512 otherwise.
  if hasattr(tsk_volume, 'info') and tsk_volume.info is not None:
    block_size = getattr(tsk_volume.info, 'block_size', 512)
  else:
    block_size = 512

  return block_size


def TSKVsPartGetNumberOfSectors(tsk_vs_part):
  """Retrieves the number of sectors of a TSK volume system part object.

  Args:
    tsk_vs_part (pytsk3.TSK_VS_PART_INFO): TSK volume system part information.

  Returns:
    int: number of sectors or None.
  """
  # Note that because pytsk3.TSK_VS_PART_INFO does not explicitly defines
  # len we need to check if the attribute exists.
  return getattr(tsk_vs_part, 'len', None)


def TSKVsPartGetStartSector(tsk_vs_part):
  """Retrieves the start sector of a TSK volume system part object.

  Args:
    tsk_vs_part (pytsk3.TSK_VS_PART_INFO): TSK volume system part information.

  Returns:
    int: start sector or None.
  """
  # Note that because pytsk3.TSK_VS_PART_INFO does not explicitly defines
  # start we need to check if the attribute exists.
  return getattr(tsk_vs_part, 'start', None)


def TSKVsPartIsAllocated(tsk_vs_part):
  """Determines if the TSK volume system part object is allocated.

  Args:
    tsk_vs_part (pytsk3.TSK_VS_PART_INFO): TSK volume system part information.

  Returns:
    bool: True if the volume system part is allocated, False otherwise.
  """
  # Note that because pytsk3.TSK_VS_PART_INFO does not explicitly defines
  # flags need to check if the attribute exists.
  # The flags are an instance of TSK_VS_PART_FLAG_ENUM.
  tsk_vs_part_flags = getattr(tsk_vs_part, 'flags', None)

  # For APM partition tables the description needs to be checked to determine
  # the usage of the part.
  tsk_vs_part_desc = getattr(tsk_vs_part, 'desc', None)

  return (tsk_vs_part_flags is not None and
          tsk_vs_part_flags == pytsk3.TSK_VS_PART_FLAG_ALLOC and
          tsk_vs_part_desc not in (b'Apple_partition_map', b'Apple_Free'))
