# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) error classes."""


class Error(Exception):
  """Generic error."""


class AccessError(Error):
  """Access error."""


class BackEndError(Error):
  """Back-end error."""


class CacheFullError(Error):
  """Cache full error."""


class FileFormatError(Error):
  """File format error."""


class MountPointError(Error):
  """Mount point error."""


class NotSupported(Error):
  """Not supported exception."""


class PathSpecError(Error):
  """Path specification error."""


class ScannerError(Error):
  """Scanner error."""


class UserAbort(Error):
  """User initiated abort exception."""


class VolumeSystemError(Error):
  """Volume system error."""
