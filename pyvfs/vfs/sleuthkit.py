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
"""This file contains the class to get a pyVFS file from an image using TSK."""
import logging
import pytsk3

from pyvfs.lib import interface


# TODO: MERGE CLASSES INTO A SINGLE ONE!!!!
class TSKFile(object):
  """Class that simulates most of the methods of a read-only file object."""
  MIN_READSIZE = 1024 * 1024

  def __init__(self, filesystem, inode, path):
    """Constructor for the TSKFile class.

    This class assumes that a filesystem using pytsk3.FS_Info has already been
    created.

    The file object that is returned can be used in most basic ways like a
    normal file object, that is the read methods. No write support is
    implemented, since the intention of this class is to provide a read-only
    interface to raw disk images.

    Args:
      filesystem: A pytsk3.FS_Info filesystem object.
      inode: An inode number for the the file.
      path: Full name (with path) of the file being opened.

    Raises:
      IOError: if the file opened does not have a metadata structure available
      or if this is a directory object instead of a file one.
    """
    self.inode = inode
    self.fs = filesystem

    # We prefer opening up a file by it's inode number.
    if inode:
      self.fileobj = self.fs.open_meta(inode=inode)
    else:
      self.fileobj = self.fs.open(path)

    self.size = self.fileobj.info.meta.size
    self.name = path
    self.ctime = self.fileobj.info.meta.ctime

    if not self.fileobj.info.meta:
      raise IOError('No valid metastructure for inode: %d' % inode)

    if self.fileobj.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG:
      raise IOError('Cannot open a directory.')

    self.readahead = ''
    self.next_read_offset = 0

  # Deviate from the naming convention since we are implementing an interface.
  def read(self, read_size=None):
    """Provide a read method for the file object.

    Args:
      read_size: An integer indicating the number of bytes to read.

    Returns:
      The content from the file, from the current offset and for read_size
      bytes.

    Raises:
      IOError: if no read_size is passed on.
    """
    if read_size is None:
      # Check file size and read within "reasonable" limits.
      if self.size - self.tell() < 1024 * 1024 * 24:
        read_size = self.size - self.tell()
      else:
        read_size = 1024 * 1024 * 24
        logging.debug(('Trying to read unbound size. Read size limited to the'
                       'maximum size of 24Mb . Size of file: %d, and current'
                       ' position in it: %d'), self.size, self.tell())

    if read_size <= len(self.readahead):
      data = self.readahead[:read_size]
      self.readahead = self.readahead[read_size:]
    else:
      data = self.readahead
      self.readahead = ''
      read_size -= len(data)
      read_now_size = min(self.size - self.tell(),
                          read_size + self.MIN_READSIZE)
      if read_now_size < 0:
        return data
      try:
        buf = self.fileobj.read_random(self.next_read_offset, read_now_size)
        self.next_read_offset += len(buf)
        self.readahead = buf[read_size:]
        data += buf[:read_size]
      except IOError:
        return data

    return data

  def IsAllocated(self):
    """Return a boolean indicating if the file is allocated or not."""
    ret = False
    flags = self.fileobj.info.meta.flags

    if flags:
      if int(flags) & int(pytsk3.TSK_FS_META_FLAG_ALLOC):
        ret = True

    return ret

  def close(self):
    """Close the file."""
    return

  def isatty(self):
    """Return a bool indicating if the file is connected to tty-like device."""
    return False

  def tell(self):
    """Return the current offset into the file."""
    return self.next_read_offset - len(self.readahead)

  def seek(self, offset, whence=0):
    """Implement a seek method.

    Set the file's current position.

    Args:
      offset: The offset to where the current position should be.
      whence: Defines whether offset is an absolute or relative
      position into the file or if it is relative to the end of the
      file.

    Raises:
      IOError:
    """
    if whence == 1:
      self.next_read_offset = self.tell() + offset
    elif whence == 2:
      self.next_read_offset = self.size + offset
    elif whence == 0:
      self.next_read_offset = offset
    else:
      raise IOError('Invalid argument for whence.')

    if self.next_read_offset < 0:
      raise IOError('Offset cannot be less than zero.')

    self.readahead = ''

  def readline(self, size=None):
    """Read a line from the file.

    Args:
      size: Defines the maximum byte count (including the new line trail)
      and if defined may get the function to return an incomplete line.

    Returns:
      A string containing a single line read from the file.
    """
    read_size = size or self.MIN_READSIZE

    # check if we need to read more into the buffer
    if '\n' not in self.readahead and read_size >= len(self.readahead):
      self.readahead = self.read(read_size)

    result, sep, self.readahead = self.readahead.partition('\n')

    return result + sep

  def readlines(self, sizehint=None):
    """Read until EOF using readline() unless sizehint is provided.

    Args:
      sizehint: Read whole lines until either EOF or number of bytes
      as defined in sizehint are reached.

    Yields:
      A list of lines.
    """
    if sizehint is None or sizehint <= 0:
      sizehint = self.MIN_READSIZE

    while sizehint > 0:
      line = self.readline(sizehint)
      if not line:
        break
      yield line
      sizehint -= len(line)

  def __iter__(self):
    """Return a generator that returns all the lines in the file."""
    while 1:
      line = self.readline()
      if not line:
        break
      yield line

  def __exit__(self, unused_type, unused_value, unused_traceback):
    """Make usable with "with" statement."""
    self.close()

  def __enter__(self):
    """Make usable with "with" statement."""
    return self


class TskFile(interface.PyVFSFile):
  """Class to open up files using TSK."""

  TYPE = 'TSK'

  def _OpenFileSystem(self, path, offset):
    """Open the filesystem object and store a copy of it for caching.

    Args:
      path: Path to the image file.
      offset: If this is a disk partition an offset to the filesystem
      is needed.

    Raises:
      IOError: If no pfile.FilesystemCache object is provided.
    """
    if not hasattr(self, '_fscache'):
      raise IOError('No FS cache provided, unable to open a file.')

    fs_obj = self._fscache.Open(path, offset)

    self._fs = fs_obj.fs

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    if hasattr(self, '_stat'):
      return self._stat

    ret = Stats()
    if not self.fh:
      return ret

    try:
      info = self.fh.fileobj.info
      meta = info.meta
    except IOError:
      return ret

    if not meta:
      return ret

    fs_type = ''
    ret.mode = getattr(meta, 'mode', None)
    ret.ino = getattr(meta, 'addr', None)
    ret.nlink = getattr(meta, 'nlink', None)
    ret.uid = getattr(meta, 'uid', None)
    ret.gid = getattr(meta, 'gid', None)
    ret.size = getattr(meta, 'size', None)
    ret.atime = getattr(meta, 'atime', None)
    ret.atime_nano = getattr(meta, 'atime_nano', None)
    ret.crtime = getattr(meta, 'crtime', None)
    ret.crtime_nano = getattr(meta, 'crtime_nano', None)
    ret.mtime = getattr(meta, 'mtime', None)
    ret.mtime_nano = getattr(meta, 'mtime_nano', None)
    ret.ctime = getattr(meta, 'ctime', None)
    ret.ctime_nano = getattr(meta, 'ctime_nano', None)
    ret.dtime = getattr(meta, 'dtime', None)
    ret.dtime_nano = getattr(meta, 'dtime_nano', None)
    ret.bkup_time = getattr(meta, 'bktime', None)
    ret.bkup_time_nano = getattr(meta, 'bktime_nano', None)
    fs_type = str(self._fs.info.ftype)

    check_allocated = getattr(self.fh.fileobj, 'IsAllocated', None)
    if check_allocated:
      ret.allocated = check_allocated()
    else:
      ret.allocated = True

    if fs_type.startswith('TSK_FS_TYPE'):
      ret.fs_type = fs_type[12:]
    else:
      ret.fs_type = fs_type

    self._stat = ret
    return ret

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf.

    This method reads the content of the PathSpec protobuf and opens
    the filehandle using the Sleuthkit (TSK).

    Args:
      filehandle: A PlasoFile object that the file is contained within.
    """
    if filehandle:
      path = filehandle
    else:
      path = self.pathspec.container_path

    if hasattr(self.pathspec, 'image_offset'):
      self._OpenFileSystem(path, self.pathspec.image_offset)
    else:
      self._OpenFileSystem(path, 0)

    inode = 0
    if hasattr(self.pathspec, 'image_inode'):
      inode = self.pathspec.image_inode

    if not hasattr(self.pathspec, 'file_path'):
      self.pathspec.file_path = 'NA_NotProvided'

    self.fh = sleuthkit.Open(
        self._fs, inode, self.pathspec.file_path)

    self.name = self.pathspec.file_path
    self.size = self.fh.size
    self.display_name = u'%s:%s' % (self.pathspec.container_path,
                                    self.pathspec.file_path)
    if filehandle:
      self.display_name = u'%s:%s' % (filehandle.name, self.display_name)


