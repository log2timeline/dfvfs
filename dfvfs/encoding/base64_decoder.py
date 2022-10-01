# -*- coding: utf-8 -*-
"""The base64 decoder implementation."""

import base64
import binascii

from dfvfs.encoding import decoder
from dfvfs.encoding import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class Base64Decoder(decoder.Decoder):
  """Base64 decoder using base64."""

  ENCODING_METHOD = definitions.ENCODING_METHOD_BASE64

  def Decode(self, encoded_data):
    """Decode the encoded data.

    Args:
      encoded_data (byte): encoded data.

    Returns:
      tuple(bytes, bytes): decoded data and remaining encoded data.

    Raises:
      BackEndError: if the base64 stream cannot be decoded.
    """
    try:
      # TODO: replace by libuna implementation or equivalent. The behavior of
      # base64.b64decode() does not raise TypeError for certain invalid base64
      # data e.g. b'\x01\x02\x03\x04\x05\x06\x07\x08' these are silently
      # ignored.
      decoded_data = base64.b64decode(encoded_data)
    except (TypeError, binascii.Error) as exception:
      raise errors.BackEndError(
          f'Unable to decode base64 stream with error: {exception!s}.')

    return decoded_data, b''


manager.EncodingManager.RegisterDecoder(Base64Decoder)
