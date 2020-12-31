# -*- coding: utf-8 -*-
"""The decoder interface."""

import abc


class Decoder(object):
  """Decoder interface."""

  # pylint: disable=redundant-returns-doc

  @abc.abstractmethod
  def Decode(self, encoded_data):
    """Decodes the encoded data.

    Args:
      encoded_data (byte): encoded data.

    Returns:
      tuple(bytes, bytes): decoded data and remaining encoded data.
    """
