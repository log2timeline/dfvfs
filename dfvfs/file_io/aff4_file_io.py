# -*- coding: utf-8 -*-
"""The AFF4 image file-like object."""

import os

from pyaff4 import container as aff4_container
from pyaff4 import data_store
from pyaff4 import lexicon
from pyaff4 import rdfvalue
from pyaff4 import zip as aff4_zip

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors


class _AFF4FileObjectAdapter(object):
  """Adapter that exposes a pyaff4 stream as a file-like object."""

  def __init__(self, location):
    """Initializes the adapter.

    Args:
      location (str): path of the AFF4 container on the host file system.
    """
    super(_AFF4FileObjectAdapter, self).__init__()
    self._location = location
    self._resolver = None
    self._stream = None
    self._stream_size = None
    self._zip_file = None
    self._zip_file_context = None

    self._Open()

  def _GetDataStream(self, image_urn, format_version, lex):
    """Retrieves the AFF4 data stream for an image.

    Args:
      image_urn (RDFURN): image URN.
      format_version (Version): AFF4 container version.
      lex (module): AFF4 lexicon module.

    Returns:
      AFF4Stream: AFF4 stream.

    Raises:
      IOError: if no readable data stream exists.
    """
    volume_urn = self._zip_file.urn
    datastreams = list(self._resolver.QuerySubjectPredicate(
        volume_urn, image_urn, lex.dataStream))

    for stream_urn in datastreams:
      if lex.map in self._resolver.QuerySubjectPredicate(
          volume_urn, stream_urn, lexicon.AFF4_TYPE):
        return self._resolver.AFF4FactoryOpen(stream_urn, version=format_version)

    raise IOError('Unable to determine AFF4 image data stream.')

  def _Open(self):
    """Opens the AFF4 image."""
    format_version, lex = aff4_container.Container.identify(self._location)

    self._resolver = data_store.MemoryDataStore(lex)

    container_urn = rdfvalue.URN.FromFileName(self._location)
    self._zip_file_context = aff4_zip.ZipFile.NewZipFile(
        self._resolver, format_version, container_urn)
    self._zip_file = self._zip_file_context.__enter__()

    image_urns = list(self._resolver.QueryPredicateObject(
        self._zip_file.urn, lexicon.AFF4_TYPE, lex.Image))
    if not image_urns:
      raise IOError('Unable to determine AFF4 image URN.')

    self._stream = self._GetDataStream(image_urns[0], format_version, lex)
    self._stream_size = self._stream.Size()

  def close(self):
    """Closes the file-like object."""
    if self._stream is not None and self._resolver is not None:
      self._stream.Close()
      self._resolver.Return(self._stream)
      self._stream = None

    if self._zip_file_context is not None:
      self._zip_file_context.__exit__(None, None, None)
      self._zip_file_context = None
      self._zip_file = None

    if self._resolver is not None:
      self._resolver.Flush()
      self._resolver = None

  def get_offset(self):
    """Retrieves the current offset."""
    return self._stream.TellRead()

  def get_size(self):
    """Retrieves the stream size."""
    return self._stream_size

  def read(self, size=None):
    """Reads data from the current offset."""
    if size is None:
      size = self._stream_size - self.get_offset()

    return self._stream.Read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset."""
    if whence not in (os.SEEK_SET, os.SEEK_CUR, os.SEEK_END):
      raise IOError(f'Unsupported whence: {whence:d}.')

    current_offset = self.get_offset()
    if whence == os.SEEK_SET:
      target_offset = offset
    elif whence == os.SEEK_CUR:
      target_offset = current_offset + offset
    else:
      target_offset = self._stream_size + offset

    if target_offset < 0:
      raise IOError('Invalid offset value less than zero.')

    self._stream.SeekRead(offset, whence)


class AFF4File(file_object_io.FileObjectIO):
  """File input/output (IO) object using pyaff4."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      _AFF4FileObjectAdapter: file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    parent_path_spec = path_spec.parent
    parent_location = getattr(parent_path_spec, 'location', None)
    if not parent_location or not parent_path_spec.IsSystemLevel():
      raise errors.PathSpecError(
          'Unsupported path specification without system-level location.')

    return _AFF4FileObjectAdapter(parent_location)
