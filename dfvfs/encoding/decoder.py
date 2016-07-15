# -*- coding: utf-8 -*-
"""The decoder object interface."""

import abc


class Decoder(object):
  """Class that implements the decoder object interface."""

  @abc.abstractmethod
  def Decode(self, encoded_data):
    """Decodes the encoded data.

    Args:
      encoded_data (byte): encoded data.

    Returns:
      tuple(bytes,bytes): decoded data and remaining encoded data.
    """
