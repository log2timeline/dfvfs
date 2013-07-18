#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This file contains the interface for VFS."""
import logging

from plaso.lib import errors
from plaso.lib import event
from plaso.lib import registry
from plaso.lib import vss
from plaso.proto import transmission_pb2

import pytsk3
import pyvshadow


class PlasoFile(object):
  """Base class for a file like object."""
  __metaclass__ = registry.MetaclassRegistry
  __abstract = True

  TYPE = 'UNSET'
  fh = None

  def __init__(self, proto, root=None, fscache=None):
    """Constructor.

    Args:
      proto: The transmission_proto that describes the file.
      root: The root transmission_proto that describes the file if one exists.
      fscache: A FilesystemCache object.

    Raises:
      errors.UnableToOpenFile: If this class supports the wrong driver for this
      file.
    """
    self.pathspec = proto
    if root:
      self.pathspec_root = root
    else:
      self.pathspec_root = proto
    self.name = ''

    if fscache:
      self._fscache = fscache

    if proto.type != self.TYPE:
      raise errors.UnableToOpenFile('Unable to handle this file type.')

  def __enter__(self):
    """Make it work with the with statement."""
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    """Make it work with the with statement."""
    _ = exc_type
    _ = exc_value
    _ = traceback
    self.close()
    return False

  def __str__(self):
    """Return a string representation of the file object, the display name."""
    if hasattr(self, 'display_name'):
      __pychecker__ = 'missingattrs=display_name'
      return self.display_name
    else:
      return 'Unknown File'

  # Implementing an interface.
  def seek(self, offset, whence=0):
    """Seek to an offset in the file."""
    if self.fh:
      self.fh.seek(offset, whence)
    else:
      raise RuntimeError('Unable to seek into a file that is not open.')

  # Implementing an interface.
  def read(self, size=None):
    """Read size bytes from file and return them."""
    if self.fh:
      # Some internal implementations require unbound read operations
      # to use a -1 as the default value, others None.
      try:
        return self.fh.read(size)
      except TypeError:
        return self.fh.read(-1)
    else:
      return ''

  # Implementing an interface.
  def tell(self):
    """Return the current offset into the file."""
    if self.fh:
      return self.fh.tell()
    else:
      return 0

  # Implementing an interface.
  def close(self):
    """Close the file."""
    if self.fh:
      self.fh.close()
      self.fh = None

  # Implementing an interface.
  def readline(self, size=None):
    """Read a line from the file.

    Args:
      size: Defines the maximum byte count (including the new line trail)
      and if defined may get the function to return an incomplete line.

    Returns:
      A string containing a single line read from the file.
    """
    if self.fh:
      return self.fh.readline(size)
    else:
      return ''

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf.

    This method reads the content of the PathSpec protobuf and opens
    the filehandle up according to the driver the class supports.

    Filehandle can be passed to the method if the file that needs to
    be opened is within another file.

    Args:
      filehandle: A PlasoFile object that the file is contained within.
    """
    raise NotImplementedError

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    raise NotImplementedError

  def HasParent(self):
    """Check if the PathSpec defines a parent."""
    return hasattr(self.pathspec, 'nested_pathspec')

  def __iter__(self):
    """Implement an iterator that reads each line."""
    line = self.readline()
    while line:
      yield line
      line = self.readline()


class Stats(object):
  """Provide an object for stat results."""

  attributes = None

  def __init__(self):
    """Constructor for the stats object."""
    self.attributes = {}

  def __setattr__(self, attr, value):
    """Sets the value to either the default or the attribute store."""
    if value is None:
      return
    try:
      object.__getattribute__(self, attr)
      object.__setattr__(self, attr, value)
    except AttributeError:
      self.attributes.__setitem__(attr, value)

  def __iter__(self):
    """Return a generator that returns key/value pairs for each attribute."""
    for key, value in sorted(self.attributes.items()):
      yield key, value

  def __getattr__(self, attr):
    """Determine if attribute is set within the event or in a container."""
    try:
      return object.__getattribute__(self, attr)
    except AttributeError:
      pass

    # Check the attribute store.
    try:
      if attr in self.attributes:
        return self.attributes.__getitem__(attr)
    except TypeError as e:
      raise AttributeError('%s', e)

    raise AttributeError('Attribute not defined')


PFILE_HANDLERS = {}


def InitPFile():
  """Creates a dict object with all PFile handlers."""
  for cl in PlasoFile.classes:
    PFILE_HANDLERS[PlasoFile.classes[cl].TYPE] = PlasoFile.classes[cl]


def OpenPFile(spec, fh=None, orig=None, fscache=None):
  """Open up a PlasoFile object.

  The location and how to open the file is described in the PathSpec protobuf
  that includes location and information about which driver to use to open it.

  Each PathSpec can also define a nested PathSpec, if that file is stored
  within another file, or even an embedded one.

  An example PathSpec describing an image file that contains a GZIP compressed
  TAR file, that contains a GZIP compressed syslog file, providing multiple
  level of nested paths.

  type: TSK
  file_path: "/logs/sys.tgz"
  container_path: "test_data/syslog_image.dd"
  image_offset: 0
  image_inode: 12
  nested_pathspec {
    type: GZIP
    file_path: "/logs/sys.tgz"
    nested_pathspec {
      type: TAR
      file_path: "syslog.gz"
      container_path: "/logs/sys.tgz"
      nested_pathspec {
        type: GZIP
        file_path: "syslog.gz"
      }
    }
  }

  Args:
    spec: A PathSpec protobuf that describes the file that needs to be opened.
    fh: A PFile object that is used as base for extracting the needed file out.
    orig: A PathSpec protobuf that describes the root pathspec of the file.
    fscache: A FilesystemCache object.

  Returns:
    A PFile object, that is a file like object.

  Raises:
    IOError: If the method is unable to open the file.
  """
  if not PFILE_HANDLERS:
    InitPFile()

  if isinstance(spec, (str, unicode)):
    spec_str = spec
    spec = event.EventPathSpec()
    spec.FromProtoString(spec_str)
  elif isinstance(spec, transmission_pb2.PathSpec):
    spec_proto = spec
    spec = event.EventPathSpec()
    spec.FromProto(spec_proto)

  handler_class = PFILE_HANDLERS.get(spec.type, 'UNSET')
  try:
    handler = handler_class(spec, orig, fscache)
  except errors.UnableToOpenFile:
    raise IOError(u'Unable to open the file: %s using %s' % (
        spec.file_path, spec.type))

  try:
    handler.Open(fh)
  except IOError as e:
    raise IOError(u'[%s] Unable to open the file: %s, error: %s' % (
        handler.__class__.__name__, spec.file_path, e))

  if hasattr(spec, 'nested_pathspec'):
    if orig:
      orig_proto = orig
    else:
      orig_proto = spec
    return OpenPFile(spec.nested_pathspec, handler, orig_proto, fscache)
  else:
    logging.debug(u'Opening file: %s [%s]', handler.name, spec.type)
    return handler

  raise IOError('Unable to open the file.')
