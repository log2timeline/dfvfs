# -*- coding: utf-8 -*-
"""The base16 decoder object implementation."""

import base64
import binascii

from dfvfs.encoding import decoder
from dfvfs.encoding import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class Base16Decoder(decoder.Decoder):
  """Class that implements a base16 decoder using base64."""

  ENCODING_METHOD = definitions.ENCODING_METHOD_BASE16

  def Decode(self, encoded_data):
    """Decode the encoded data.

    Args:
      encoded_data: a byte string containing the encoded data.

    Returns:
      A tuple containing a byte string of the decoded data and
      the remaining encoded data.

    Raises:
      BackEndError: if the base16 stream cannot be decoded.
    """
    try:
      decoded_data = base64.b16decode(encoded_data, casefold=False)
    except (TypeError, binascii.Error) as exception:
      raise errors.BackEndError(
          u'Unable to decode base16 stream with error: {0!s}.'.format(
              exception))

    return decoded_data, b''


# Register the decoder with the encoding manager.
manager.EncodingManager.RegisterDecoder(Base16Decoder)
