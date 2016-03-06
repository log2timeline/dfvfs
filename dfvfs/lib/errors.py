# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) error classes."""


class Error(Exception):
  """Class that defines a generic error."""


class AccessError(Error):
  """Class that defines access errors."""


class BackEndError(Error):
  """Class that defines back-end errors."""


class CacheFullError(Error):
  """Class that defines cache full errors."""


class FileFormatError(Error):
  """Class that defines file format errors."""


class MountPointError(Error):
  """Class that defines mount point errors."""


class PathSpecError(Error):
  """Class that defines path specification errors."""


class ScannerError(Error):
  """Class that defines scanner errors."""


class UserAbort(Error):
  """Class that defines an user initiated abort exception."""


class VolumeSystemError(Error):
  """Class that defines volume system errors."""
