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
import logging

from pyvfs.lib import errors
from pyvfs.lib import interface
from pyvfs.proto import transmission_pb2

# Add all new PyVFS handles here.
from pyvfs.vfs import bz2_compress
from pyvfs.vfs import filesystem
from pyvfs.vfs import gz_compress
try:
  from pyvfs.vfs import sleuthkit
except ImportError:
  logging.warning('No Sleuthkit support, unable to read image files.')
from pyvfs.vfs import tar_compress
try:
  from pyvfs.vfs import vss
except ImportError:
  logging.warning('No VSS support, unable to read image files.')
from pyvfs.vfs import zip_compress


class PyVfsManager(object):
  """A simple class that maintains open pfile handlers."""
  pfile_handlers = {}

  @classmethod
  def BuildHandlerList(cls):
    """Creates a dict object with all PyVFSFile handlers."""
    for cl in interface.PyVFSFile.classes:
      cls.pfile_handlers[interface.PyVFSFile.classes[
          cl].TYPE] = interface.PyVFSFile.classes[cl]

  @classmethod
  def GetHandler(cls, spec, orig, fscache):
    """Return a VFS handler if one is available for the supplied type.

    Args:
      spec: An interface.PyPathSpec object describing the file to open.

    Returns:
      A PyVFS file like object.
    """
    handler_class = cls.pfile_handlers.get(spec.type, None)

    if not handler_class:
      raise IOError(u'Unable to open file, unsupported type: {}'.format(
          spec.type))

    try:
      handler = handler_class(spec, orig, fscache)
    except errors.UnableToOpenFile:
      raise IOError(u'Unable to open the file: %s using %s' % (
          spec.file_path, spec.type))

    return handler


def OpenPyVFSFile(spec, fh=None, orig=None, fscache=None):
  """Open up a PyVFSFile object.

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
    fh: A PyVFSFile object that is used as base for extracting the needed file out.
    orig: A PathSpec protobuf that describes the root pathspec of the file.
    fscache: A FilesystemCache object.

  Returns:
    A PyVFSFile object, that is a file like object.

  Raises:
    IOError: If the method is unable to open the file.
  """
  if not PyVfsManager.pfile_handlers:
    PyVfsManager.BuildHandlerList()

  if isinstance(spec, (str, unicode)):
    spec_str = spec
    spec = interface.PyPathSpec()
    spec.FromProtoString(spec_str)
  elif isinstance(spec, transmission_pb2.PathSpec):
    spec_proto = spec
    spec = interface.PyPathSpec()
    spec.FromProto(spec_proto)

  handler = PyVfsManager.GetHandler(spec, orig, fscache)

  try:
    handler.Open(fh)
  except IOError as e:
    raise IOError(u'[%s] Unable to open the file: %s, error: %s' % (
        handler.handler_name, spec.file_path, e))

  if hasattr(spec, 'nested_pathspec'):
    if orig:
      orig_proto = orig
    else:
      orig_proto = spec
    return OpenPyVFSFile(spec.nested_pathspec, handler, orig_proto, fscache)
  else:
    logging.debug(u'Opening file: %s [%s]', handler.name, spec.type)
    return handler

  raise IOError('Unable to open the file.')
