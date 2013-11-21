#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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
"""Sleuthkit (TSK) image info object for Volume Shadow Snapshots (VSS)."""

import logging
import os

import pytsk3
import pyvshadow


class VShadowVolume(object):
  """File-like object that maps a specific range within a file.

     This allows to expose e.g. a volume in a full disk image as a file-like
     object.
  """

  SECTOR_SIZE = 512

  def __init__(self, file_path, offset=0):
    """Provide a file like object of a volume inside a disk image.

    Args:
      file_path: String, denoting the file path to the disk image.
      offset: An offset in bytes to the volume within the disk.
    """
    self._block_size = 0
    self._offset_start = 0
    self._orig_offset = offset

    ofs = int(offset / self.SECTOR_SIZE)
    self._block_size, self._image_size = self.GetImageSize(file_path, ofs)

    self._file_object = open(file_path, 'rb')
    self._file_object.seek(0, os.SEEK_END)
    self._file_object_size = self._file_object.tell()
    self._image_offset = ofs

    if self._block_size:
      self._offset_start = self._image_offset * self._block_size
      self._file_object.seek(self._offset_start, os.SEEK_SET)

  def GetImageSize(self, file_path, offset):
    """Read the partition information to gather volume size."""
    if not offset:
      return 0, 0

    img = pytsk3.Img_Info(file_path)
    try:
      volume = pytsk3.Volume_Info(img)
    except IOError:
      return 0, 0

    size = 0
    for vol in volume:
      if vol.start == offset:
        size = vol.len
        break

    size *= volume.info.block_size
    return volume.info.block_size, size

  def read(self, size=None):
    """"Return read bytes from volume as denoted by the size parameter."""
    if not self._orig_offset:
      return self._file_object.read(size)

    # Check upper bounds, we need to return empty values for above bounds.
    if size + self.tell() > self._offset_start + self._image_size:
      size = self._offset_start + self._image_size - self.tell()

      if size < 1:
        return ''

    return self._file_object.read(size)

  def get_size(self):
    """Return the size in bytes of the volume."""
    if self._block_size:
      return self._block_size * self._image_size

    return self._file_object_size

  def close(self):
    self._file_object.close()

  def seek(self, offset, whence=os.SEEK_SET):
    """Seek into the volume."""
    if not self._block_size:
      self._file_object.seek(offset, whence)
      return

    ofs = 0
    abs_ofs = 0
    if whence == os.SEEK_SET:
      ofs = offset + self._offset_start
      abs_ofs = ofs
    elif whence == os.SEEK_CUR:
      ofs = offset
      abs_ofs = self.tell() + ofs
    elif whence == os.SEEK_END:
      size_diff = (self._file_object_size -
          (self._offset_start + self._image_size))
      ofs = offset - size_diff
      abs_ofs = self._image_size + self._offset_start + offset
    else:
      raise RuntimeError('Illegal whence value %s' % whence)

    # check boundary
    if abs_ofs < self._offset_start:
      raise IOError('Invalid seek, out of bounds. Seek before start.')

    self._file_object.seek(ofs, whence)

  def tell(self):
    if not self._block_size:
      return self._file_object.tell()

    return self._file_object.tell() - self._offset_start

  def get_offset(self):
    return self.tell()


def GetVssStoreCount(image, offset=0):
  """Return the number of VSS stores available in an image."""
  volume = pyvshadow.volume()
  file_object = VShadowVolume(image, offset)
  try:
    volume.open_file_object(file_object)
    return volume.number_of_stores
  except IOError as e:
    logging.warning('Error while trying to read VSS information: %s', e)

  return 0
