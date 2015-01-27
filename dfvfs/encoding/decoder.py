# -*- coding: utf-8 -*-
"""The decoder object interface."""

import abc


class Decoder(object):
  """Class that implements the decoder object interface."""

  @abc.abstractmethod
  def Decode(self, encoded_data):
    """Decodes the encoded data.

    Args:
      encoded_data: a byte string containing the encoded data.

    Returns:
      A tuple containing a byte string of the decoded data and
      the remaining encoded data.
    """
