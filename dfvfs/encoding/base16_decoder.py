# -*- coding: utf-8 -*-
"""The base16 decoder implementation."""

import base64
import binascii

from dfvfs.encoding import decoder
from dfvfs.encoding import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class Base16Decoder(decoder.Decoder):
  """Base16 decoder using base64."""

  ENCODING_METHOD = definitions.ENCODING_METHOD_BASE16

  def Decode(self, encoded_data):
    """Decode the encoded data.

    Args:
      encoded_data (byte): encoded data.

    Returns:
      tuple(bytes, bytes): decoded data and remaining encoded data.

    Raises:
      BackEndError: if the base16 stream cannot be decoded.
    """
    try:
      decoded_data = base64.b16decode(encoded_data, casefold=False)
    except (TypeError, binascii.Error) as exception:
      raise errors.BackEndError(
          f'Unable to decode base16 stream with error: {exception!s}.')

    return decoded_data, b''


manager.EncodingManager.RegisterDecoder(Base16Decoder)
