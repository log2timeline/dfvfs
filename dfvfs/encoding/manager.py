# -*- coding: utf-8 -*-
"""The encoding manager."""


class EncodingManager(object):
  """Encoding manager."""

  _decoders = {}

  @classmethod
  def DeregisterDecoder(cls, decoder):
    """Deregisters a decoder for a specific encoding method.

    Args:
      decoder (type): decoder class.

    Raises:
      KeyError: if the corresponding decoder is not set.
    """
    encoding_method = decoder.ENCODING_METHOD.lower()
    if encoding_method not in cls._decoders:
      raise KeyError(
          f'Decoder for encoding method: {decoder.ENCODING_METHOD:s} not set.')

    del cls._decoders[encoding_method]

  @classmethod
  def GetDecoder(cls, encoding_method):
    """Retrieves the decoder object for a specific encoding method.

    Args:
      encoding_method (str): encoding method identifier.

    Returns:
      Decoder: decoder or None if the encoding method does not exists.
    """
    encoding_method = encoding_method.lower()
    decoder = cls._decoders.get(encoding_method, None)
    if not decoder:
      return None

    return decoder()

  @classmethod
  def RegisterDecoder(cls, decoder):
    """Registers a decoder for a specific encoding method.

    Args:
      decoder (type): decoder class.

    Raises:
      KeyError: if the corresponding decoder is already set.
    """
    encoding_method = decoder.ENCODING_METHOD.lower()
    if encoding_method in cls._decoders:
      raise KeyError((
          f'Decoder for encoding method: {decoder.ENCODING_METHOD:s} already '
          f'set.'))

    cls._decoders[encoding_method] = decoder

  @classmethod
  def RegisterDecoders(cls, decoders):
    """Registers decoders.

    The decoders are identified based on their lower case encoding method.

    Args:
      decoders (list[type]): decoder classes.

    Raises:
      KeyError: if decoders is already set for the corresponding
          encoding method.
    """
    for decoder in decoders:
      cls.RegisterDecoder(decoder)
