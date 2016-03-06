# -*- coding: utf-8 -*-
"""The BZIP2 decompressor object implementation."""

import bz2

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class BZIP2Decompressor(decompressor.Decompressor):
  """Class that implements a BZIP2 decompressor using bz2."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_BZIP2

  def __init__(self):
    """Initializes the decompressor object."""
    super(BZIP2Decompressor, self).__init__()
    self._bz2_decompressor = bz2.BZ2Decompressor()

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.

    Raises:
      BackEndError: if the BZIP2 compressed stream cannot be decompressed.
    """
    try:
      uncompressed_data = self._bz2_decompressor.decompress(compressed_data)
      remaining_compressed_data = getattr(
          self._bz2_decompressor, u'unused_data', b'')

    except (EOFError, IOError) as exception:
      raise errors.BackEndError((
          u'Unable to decompress BZIP2 compressed stream with error: '
          u'{0!s}.').format(exception))

    return uncompressed_data, remaining_compressed_data


manager.CompressionManager.RegisterDecompressor(BZIP2Decompressor)
