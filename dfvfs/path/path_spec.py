"""The Virtual File System (VFS) path specification interface."""

import functools

from dfvfs.lib import definitions

# Name of the instance attribute that caches the comparable, which is excluded from
# the path specification attributes.
_COMPARABLE_CACHE_NAME = "_comparable_cache"

# Mutation epoch, incremented every time an attribute of a path specification that
# has a cached comparable is changed. A cached comparable is only valid for the epoch
# it was computed in, which also covers changes to (grand)parent path specifications.
_MUTATION_EPOCH = [0]


def _CachedComparable(comparable_function):
    """Wraps a comparable property getter to cache the result per instance.

    Args:
      comparable_function (function): comparable property getter.

    Returns:
      function: comparable property getter that caches its result.
    """

    @functools.wraps(comparable_function)
    def GetCachedComparable(path_spec):
        """Retrieves the cached comparable representation."""
        cache = path_spec.__dict__.get(_COMPARABLE_CACHE_NAME, None)
        if cache and cache[0] == _MUTATION_EPOCH[0]:
            return cache[1]

        comparable = comparable_function(path_spec)
        path_spec.__dict__[_COMPARABLE_CACHE_NAME] = (_MUTATION_EPOCH[0], comparable)
        return comparable

    GetCachedComparable.is_cached_comparable = True
    return GetCachedComparable


class PathSpec:
    """Path specification interface.

    Attributes:
      parent (PathSpec): parent path specification.
    """

    # pylint: disable=missing-raises-doc

    _IS_SYSTEM_LEVEL = False

    def __init_subclass__(cls, **kwargs):
        """Wraps the comparable property of a derived class to cache its value."""
        super().__init_subclass__(**kwargs)

        comparable_property = cls.__dict__.get("comparable", None)
        if isinstance(comparable_property, property) and not getattr(
            comparable_property.fget, "is_cached_comparable", False
        ):
            cls.comparable = property(
                _CachedComparable(comparable_property.fget),
                doc=comparable_property.__doc__,
            )

    def __init__(self, parent=None, **kwargs):
        """Initializes a path specification.

        Args:
          parent (Optional[PathSpec]): parent path specification.
          kwargs (dict[str, object]): keyword arguments depending on the path
              specification.

        Raises:
          ValueError: if a derived path specification class does not define a type
              indicator or when there are unused keyword arguments.
        """
        if kwargs:
            keyword_arguments = ", ".join(kwargs)
            raise ValueError(f"Unused keyword arguments: {keyword_arguments:s}.")

        super().__init__()
        self.parent = parent

        if not getattr(self, "TYPE_INDICATOR", None):
            raise ValueError("Missing type indicator.")

    def __eq__(self, other):
        """Determines if the path specification is equal to the other."""
        if self is other:
            return True
        return isinstance(other, PathSpec) and self.comparable == other.comparable

    def __hash__(self):
        """Returns the hash of a path specification."""
        return hash(self.comparable)

    def __setattr__(self, name, value):
        """Sets an attribute and invalidates cached comparables if needed."""
        if name != _COMPARABLE_CACHE_NAME and _COMPARABLE_CACHE_NAME in self.__dict__:
            # Comparables of child path specifications include this one.
            _MUTATION_EPOCH[0] += 1
            del self.__dict__[_COMPARABLE_CACHE_NAME]
        super().__setattr__(name, value)

    def _GetComparable(self, sub_comparable_string=""):
        """Retrieves the comparable representation.

        This is a convenience function for constructing comparables.

        Args:
          sub_comparable_string (str): sub comparable string.

        Returns:
          str: comparable representation of the path specification.
        """
        string_parts = []

        string_parts.append(getattr(self.parent, "comparable", ""))
        string_parts.append(f"type: {self.type_indicator:s}")

        if sub_comparable_string:
            string_parts.append(f", {sub_comparable_string:s}")
        string_parts.append("\n")

        return "".join(string_parts)

    @property
    @_CachedComparable
    def comparable(self):
        """str: comparable representation of the path specification."""
        return self._GetComparable()

    @property
    def type_indicator(self):
        """str: type indicator."""
        # pylint: disable=no-member
        return self.TYPE_INDICATOR

    def CopyToDict(self):
        """Copies the path specification to a dictionary.

        Returns:
          dict[str, object]: path specification attributes.
        """
        path_spec_dict = {}
        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_value is None or attribute_name == _COMPARABLE_CACHE_NAME:
                continue

            if attribute_name == "parent":
                attribute_value = attribute_value.CopyToDict()

            path_spec_dict[attribute_name] = attribute_value

        return path_spec_dict

    def HasParent(self):
        """Determines if the path specification has a parent.

        Returns:
          bool: True if the path specification has a parent.
        """
        return self.parent is not None

    def IsFileSystem(self):
        """Determines if the path specification is a file system.

        Returns:
          bool: True if the path specification is a file system.
        """
        return self.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS

    def IsSystemLevel(self):
        """Determines if the path specification is at system-level.

        System-level is an indication used if the path specification is
        handled by the operating system and should not have a parent.

        Returns:
          bool: True if the path specification is at system-level.
        """
        return getattr(self, "_IS_SYSTEM_LEVEL", False)

    def IsVolumeSystem(self):
        """Determines if the path specification is a volume system.

        Returns:
          bool: True if the path specification is a volume system.
        """
        return self.type_indicator in definitions.VOLUME_SYSTEM_TYPE_INDICATORS

    def IsVolumeSystemRoot(self):
        """Determines if the path specification is the root of a volume system.

        Returns:
          bool: True if the path specification is the root of a volume system.
        """
        return self.IsVolumeSystem() and getattr(self, "location", None) == "/"
