"""The ZIP archive file path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class ZipPathSpec(location_path_spec.LocationPathSpec):
    """ZIP archive file path specification."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

    def __init__(self, archive_path=None, location=None, parent=None, **kwargs):
        """Initializes a path specification.

        Note that the zip file path specification must have a parent.

        Args:
          archive_path (Optional[str]): path as stored in the ZIP archive.
          location (Optional[str]): ZIP file internal location string prefixed
              with a path separator character.
          parent (Optional[PathSpec]): parent path specification.

        Raises:
          ValueError: when parent is not set.
        """
        if not parent:
            raise ValueError("Missing parent value.")

        super().__init__(location=location, parent=parent, **kwargs)
        self.archive_path = archive_path

    @property
    def comparable(self):
        """str: comparable representation of the path specification."""
        sub_comparable_parts = [f"location: {self.location:s}"]
        if self.archive_path is not None:
            sub_comparable_parts.append(f"archive path: {self.archive_path:s}")

        return self._GetComparable(
            sub_comparable_string=", ".join(sub_comparable_parts)
        )


factory.Factory.RegisterPathSpec(ZipPathSpec)
