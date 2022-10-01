# -*- coding: utf-8 -*-
"""The path specification mount point manager.

The mount point manager allows to "mount" one path specification onto another.
This allows dfVFS to expose complex path specifications in a way closer to
the original system interpretation.

E.g. the path specification:
type=OS, location=/home/myuser/myimages/image.qcow2
type=QCOW
type=TSK_PARTITION, location=/p1
type=TSK, inode=128, location=/Users/MyUser/MyFile.txt

could be mounted as:
type=MOUNT, identifier=C
type=TSK, inode=128, location=/Users/MyUser/MyFile.txt

where the "C" mount point would be:
type=OS, location=/home/myuser/myimages/image.qcow2
type=QCOW
type=TSK_PARTITION, location=/p1
"""


class MountPointManager(object):
  """Path specification mount point manager."""

  _mount_points = {}

  @classmethod
  def DeregisterMountPoint(cls, mount_point):
    """Deregisters a path specification mount point.

    Args:
      mount_point (str): mount point identifier.

    Raises:
      KeyError: if the corresponding mount point is not set.
    """
    if mount_point not in cls._mount_points:
      raise KeyError(f'Mount point: {mount_point:s} not set.')

    del cls._mount_points[mount_point]

  @classmethod
  def GetMountPoint(cls, mount_point):
    """Retrieves the path specification of a mount point.

    Args:
      mount_point (str): mount point identifier.

    Returns:
      PathSpec: path specification of the mount point or None if the mount
          point does not exists.
    """
    return cls._mount_points.get(mount_point, None)

  @classmethod
  def RegisterMountPoint(cls, mount_point, path_spec):
    """Registers a path specification mount point.

    Args:
      mount_point (str): mount point identifier.
      path_spec (PathSpec): path specification of the mount point.

    Raises:
      KeyError: if the corresponding mount point is already set.
    """
    if mount_point in cls._mount_points:
      raise KeyError(f'Mount point: {mount_point:s} already set.')

    cls._mount_points[mount_point] = path_spec
