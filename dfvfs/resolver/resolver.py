# -*- coding: utf-8 -*-
"""The path specification resolver."""

from dfvfs.credentials import keychain
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.mount import manager as mount_manager
from dfvfs.resolver import context


class Resolver(object):
  """Class that implements the path specification resolver."""

  _resolver_context = context.Context()
  _resolver_helpers = {}

  key_chain = keychain.KeyChain()

  @classmethod
  def DeregisterHelper(cls, resolver_helper):
    """Deregisters a path specification resolver helper.

    Args:
      resolver_helper: the resolver helper object (instance of
                       ResolverHelper).

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
    """
    if resolver_helper.type_indicator not in cls._resolver_helpers:
      raise KeyError(
          u'Resolver helper object not set for type indicator: {0:s}.'.format(
              resolver_helper.type_indicator))

    del cls._resolver_helpers[resolver_helper.type_indicator]

  @classmethod
  def OpenFileEntry(cls, path_spec, resolver_context=None):
    """Opens a file entry object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file entry object (instance of vfs.FileEntry) or None if the path
      specification could not be resolved.
    """
    file_system = cls.OpenFileSystem(
        path_spec, resolver_context=resolver_context)

    if resolver_context is None:
      resolver_context = cls._resolver_context

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    # Release the file system so it will be removed from the cache
    # when the file entry is destroyed.
    resolver_context.ReleaseFileSystem(file_system)

    return file_entry

  @classmethod
  def OpenFileObject(cls, path_spec, resolver_context=None):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file-like object (instance of file.FileIO) or None if the path
      specification could not be resolved.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
      PathSpecError: if the path specification is incorrect.
    """
    if resolver_context is None:
      resolver_context = cls._resolver_context

    if path_spec.type_indicator == definitions.TYPE_INDICATOR_MOUNT:
      if path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported mount path specification with parent.')

      mount_point = getattr(path_spec, u'identifier', None)
      if not mount_point:
        raise errors.PathSpecError(
            u'Unsupported path specification without mount point identifier.')

      path_spec = mount_manager.MountPointManager.GetMountPoint(mount_point)
      if not path_spec:
        raise errors.MountPointError(
            u'No such mount point: {0:s}'.format(mount_point))

    file_object = resolver_context.GetFileObject(path_spec)
    if not file_object:
      if path_spec.type_indicator not in cls._resolver_helpers:
        raise KeyError((
            u'Resolver helper object not set for type indicator: '
            u'{0:s}.').format(path_spec.type_indicator))

      resolver_helper = cls._resolver_helpers[path_spec.type_indicator]
      file_object = resolver_helper.NewFileObject(resolver_context)

    file_object.open(path_spec=path_spec)
    return file_object

  @classmethod
  def OpenFileSystem(cls, path_spec, resolver_context=None):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.

    Returns:
      The file system object (instance of vfs.FileSystem) or None if the path
      specification could not be resolved or has no file system object.

    Raises:
      AccessError: if the access to open the file system was denied.
      BackEndError: if the file system cannot be opened.
      KeyError: if resolver helper object is not set for the corresponding
                type indicator.
      PathSpecError: if the path specification is incorrect.
    """
    if resolver_context is None:
      resolver_context = cls._resolver_context

    if path_spec.type_indicator == definitions.TYPE_INDICATOR_MOUNT:
      if path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported mount path specification with parent.')

      mount_point = getattr(path_spec, u'identifier', None)
      if not mount_point:
        raise errors.PathSpecError(
            u'Unsupported path specification without mount point identifier.')

      path_spec = mount_manager.MountPointManager.GetMountPoint(mount_point)
      if not path_spec:
        raise errors.MountPointError(
            u'No such mount point: {0:s}'.format(mount_point))

    file_system = resolver_context.GetFileSystem(path_spec)
    if not file_system:
      if path_spec.type_indicator not in cls._resolver_helpers:
        raise KeyError((
            u'Resolver helper object not set for type indicator: '
            u'{0:s}.').format(path_spec.type_indicator))

      resolver_helper = cls._resolver_helpers[path_spec.type_indicator]
      file_system = resolver_helper.NewFileSystem(resolver_context)

    try:
      file_system.Open(path_spec)
    except (errors.AccessError, errors.PathSpecError):
      raise
    except (IOError, ValueError) as exception:
      raise errors.BackEndError(
          u'Unable to open file system with error: {0:s}'.format(exception))

    return file_system

  @classmethod
  def RegisterHelper(cls, resolver_helper):
    """Registers a path specification resolver helper.

    Args:
      resolver_helper: the resolver helper object (instance of
                       ResolverHelper).

    Raises:
      KeyError: if resolver helper object is already set for the corresponding
                type indicator.
    """
    if resolver_helper.type_indicator in cls._resolver_helpers:
      raise KeyError((
          u'Resolver helper object already set for type indicator: '
          u'{0!s}.').format(resolver_helper.type_indicator))

    cls._resolver_helpers[resolver_helper.type_indicator] = resolver_helper
