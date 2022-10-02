# -*- coding: utf-8 -*-
"""The zlib and DEFLATE decompressor implementations."""

import zlib

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class ZlibDecompressor(decompressor.Decompressor):
  """DEFLATE with zlib data decompressor using zlib."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_ZLIB

  def __init__(self, window_size=zlib.MAX_WBITS):
    """Initializes a decompressor.

    Args:
      window_size (Optional[int]): base two logarithm of the size of
          the compression history buffer (aka window size). When the value
          is negative, the standard zlib data header is suppressed.
    """
    super(ZlibDecompressor, self).__init__()
    self._zlib_decompressor = zlib.decompressobj(window_size)

  @property
  def unused_data(self):
    """bytes: data past the end of the compressed data."""
    return self._zlib_decompressor.unused_data

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes, bytes): uncompressed data and remaining compressed data.

    Raises:
      BackEndError: if the zlib compressed stream cannot be decompressed.
    """
    try:
      uncompressed_data = self._zlib_decompressor.decompress(compressed_data)
      remaining_compressed_data = getattr(
          self._zlib_decompressor, 'unused_data', b'')

    except zlib.error as exception:
      raise errors.BackEndError((
          f'Unable to decompress zlib compressed stream with error: '
          f'{exception!s}.'))

    return uncompressed_data, remaining_compressed_data


class DeflateDecompressor(ZlibDecompressor):
  """DEFLATE without zlib data decompressor using zlib."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_DEFLATE

  def __init__(self):
    """Initializes a decompressor."""
    super(DeflateDecompressor, self).__init__(window_size=-zlib.MAX_WBITS)


manager.CompressionManager.RegisterDecompressors([
    DeflateDecompressor, ZlibDecompressor])
