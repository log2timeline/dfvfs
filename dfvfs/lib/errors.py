# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) error classes."""


class Error(Exception):
  """Parent class for dfVFS specific errors."""


class AccessError(Error):
  """Error indicating that a resource could not be accessed."""


class BackEndError(Error):
  """Error indicating that a dependency has encountered a problem."""


class CacheFullError(Error):
  """Error indicating a cache is full."""


class FileFormatError(Error):
  """Error indicating a problem in the format of a file."""


class MountPointError(Error):
  """Error indicating a mount point does not exist."""


class NotSupported(Error):
  """Error indicating that unsupported functionality was requested."""


class PathSpecError(Error):
  """Error indicating a problem with a path specification."""


class ScannerError(Error):
  """Error indicating that an item could not be scanned."""


class UserAbort(Error):
  """Exception indicating that the user initiated an abort."""


class VolumeSystemError(Error):
  """Error indicating a problem with a volume system."""
