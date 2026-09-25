# -*- coding: utf-8 -*-
"""The Keramics path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class KeramicsPathSpec(path_spec.PathSpec):
    """Keramics path specification.

    Attributes:
      location (str): location.
    """

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_KERAMICS

    def __init__(self, location=None, parent=None, **kwargs):
        """Initializes a path specification.

        Args:
          location (Optional[str]): location.
          parent (Optional[PathSpec]): parent path specification.

        Raises:
          ValueError: when location is not set.
        """
        if not location:
            raise ValueError("Missing location.")

        super().__init__(parent=parent, **kwargs)
        self.location = location

    @property
    def comparable(self):
        """str: comparable representation of the path specification."""
        # TODO: handle Keramics location.
        location_string = str(self.location)
        string_parts = [f"location: {location_string:s}"]
        return self._GetComparable(sub_comparable_string=", ".join(string_parts))


factory.Factory.RegisterPathSpec(KeramicsPathSpec)
