# -*- coding: utf-8 -*-
"""The format specification classes."""


class Signature(object):
  """Signature of a format specification.

  The signature consists of a byte string pattern, an optional
  offset relative to the start of the data, and a value to indicate
  if the pattern is bound to the offset.

  Attributes:
    identifier (str): unique signature identifier for a specification store.
    offset (int): offset of the signature, where None indicates the signature
          has no offset. A positive offset or 0 is relative to the start of
          the data a negative offset is relative to the end of the data.
    pattern (bytes): pattern of the signature.
  """

  def __init__(self, pattern, offset=None):
    """Initializes a signature.

    Args:
      pattern (bytes): pattern of the signature. Wildcards or regular pattern
          (regexp) are not supported.
      offset (Optional[int]): offset of the signature, where None indicates
          the signature has no offset. A positive offset or 0 is relative
          from the start of the data a negative offset is relative to
          the end of the data.
    """
    super(Signature, self).__init__()
    self.identifier = None
    self.offset = offset
    self.pattern = pattern

  def SetIdentifier(self, identifier):
    """Sets the identifier of the signature in the specification store.

    Args:
      identifier (str): unique signature identifier for a specification store.
    """
    self.identifier = identifier


class FormatSpecification(object):
  """Format specification."""

  def __init__(self, identifier):
    """Initializes a specification.

    Args:
      identifier (str): unique name for the format.
    """
    super(FormatSpecification, self).__init__()
    self.identifier = identifier
    self.signatures = []

  def AddNewSignature(self, pattern, offset=None):
    """Adds a signature.

    Args:
      pattern (bytes): pattern of the signature. Wildcards or regular pattern
          (regexp) are not supported.
      offset (Optional[int]): offset of the signature, where None indicates
          the signature has no offset. A positive offset or 0 is relative
          from the start of the data a negative offset is relative to
          the end of the data.
    """
    self.signatures.append(Signature(pattern, offset=offset))


class FormatSpecificationStore(object):
  """Store for format specifications."""

  def __init__(self):
    """Initializes a format specification store."""
    super(FormatSpecificationStore, self).__init__()
    self._format_specifications = {}
    # Maps signature identifiers to format specifications.
    self._signature_map = {}

  @property
  def specifications(self):
    """generator[FormatSpecification]: format specifications."""
    return iter(self._format_specifications.values())

  def AddNewSpecification(self, identifier):
    """Adds a new format specification.

    Args:
      identifier (str): unique signature identifier for a specification store.

    Returns:
      FormatSpecification: format specification.

    Raises:
      KeyError: if the store already contains a specification with
          the same identifier.
    """
    if identifier in self._format_specifications:
      raise KeyError(
          f'Format specification {identifier:s} is already defined in store.')

    self._format_specifications[identifier] = FormatSpecification(identifier)

    return self._format_specifications[identifier]

  def AddSpecification(self, specification):
    """Adds a specification.

    Args:
      specification (FormatSpecification): format specification.

    Raises:
      KeyError: if the store already contains a specification with
          the same identifier.
    """
    if specification.identifier in self._format_specifications:
      raise KeyError((
          f'Format specification {specification.identifier:s} is already '
          f'defined in store.'))

    self._format_specifications[specification.identifier] = specification

    for signature in specification.signatures:
      signature_index = len(self._signature_map)

      signature_identifier = f'{specification.identifier:s}:{signature_index:d}'
      if signature_identifier in self._signature_map:
        raise KeyError(
            f'Signature {signature_identifier:s} is already defined in map.')

      signature.SetIdentifier(signature_identifier)
      self._signature_map[signature_identifier] = specification

  def GetSpecificationBySignature(self, signature_identifier):
    """Retrieves a specification mapped to a signature identifier.

    Args:
      signature_identifier (str): unique signature identifier for
          a specification store.

    Returns:
      FormatSpecification: A format specification or None if the signature
          identifier does not exist within the specification store.
    """
    return self._signature_map.get(signature_identifier, None)
