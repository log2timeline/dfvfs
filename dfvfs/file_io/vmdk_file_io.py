"""The VMDK image file-like object."""

import pyvmdk

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


class VMDKFile(file_object_io.FileObjectIO):
    """File input/output (IO) object using pyvmdk."""

    _MAXIMUM_PARENT_DEPTH = 32

    # Content identifier of the parent image of an image without parent image.
    _NO_PARENT_CONTENT_IDENTIFIER = 0xFFFFFFFF

    def __init__(self, resolver_context, path_spec):
        """Initializes a file input/output (IO) object.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.
        """
        super().__init__(resolver_context, path_spec)
        self._parent_vmdk_handles = []

    def _Close(self):
        """Closes the file-like object."""
        super()._Close()

        for vmdk_handle in self._parent_vmdk_handles:
            vmdk_handle.close()

        self._parent_vmdk_handles = []

    def _GetParentFilename(self, vmdk_handle):
        """Retrieves the filename of the parent image.

        The parent filename hint is stored in the descriptor and therefore is
        untrusted. Only the last path segment is used, so that the parent image
        is always looked up next to the descriptor.

        Args:
          vmdk_handle (pyvmdk.handle): VMDK handle.

        Returns:
          str: filename of the parent image.

        Raises:
          OSError: if the parent filename is not supported.
        """
        parent_filename = vmdk_handle.parent_filename or ""
        parent_filename = parent_filename.replace("\\", "/")
        _, _, parent_filename = parent_filename.rpartition("/")

        if parent_filename in ("", ".", "..") or ":" in parent_filename:
            raise OSError("Unsupported parent image filename.")

        return parent_filename

    def _HasParentImage(self, vmdk_handle):
        """Determines if a VMDK image has a parent image.

        Args:
          vmdk_handle (pyvmdk.handle): VMDK handle.

        Returns:
          bool: True if the VMDK image has a parent image.
        """
        return bool(
            vmdk_handle.parent_filename
            and vmdk_handle.parent_content_identifier
            != self._NO_PARENT_CONTENT_IDENTIFIER
        )

    def _OpenFileObject(self, path_spec):
        """Opens the file-like object defined by path specification.

        Args:
          path_spec (PathSpec): path specification.

        Returns:
          pyvmdk.handle: a file-like object.

        Raises:
          OSError: if the file-like object could not be opened.
          PathSpecError: if the path specification is incorrect.
        """
        if not path_spec.HasParent():
            raise errors.PathSpecError("Unsupported path specification without parent.")

        parent_path_spec = path_spec.parent

        parent_location = getattr(parent_path_spec, "location", None)
        if not parent_location:
            raise errors.PathSpecError(
                "Unsupported parent path specification without location."
            )

        file_system = resolver.Resolver.OpenFileSystem(
            parent_path_spec, resolver_context=self._resolver_context
        )
        vmdk_handle = self._OpenVMDKHandle(file_system, parent_path_spec)

        if self._HasParentImage(vmdk_handle):
            try:
                self._OpenParentImage(file_system, parent_path_spec, vmdk_handle)

            except (OSError, errors.PathSpecError):
                vmdk_handle.close()
                for parent_vmdk_handle in self._parent_vmdk_handles:
                    parent_vmdk_handle.close()

                self._parent_vmdk_handles = []
                raise

        return vmdk_handle

    def _OpenParentImage(self, file_system, path_spec, vmdk_handle, depth=1):
        """Opens the parent image.

        Args:
          file_system (FileSystem): file system of the VMDK descriptor file.
          path_spec (PathSpec): path specification of the VMDK descriptor file.
          vmdk_handle (pyvmdk.handle): VMDK handle.
          depth (Optional[int]): depth of the parent image in the chain.

        Raises:
          OSError: if the parent image could not be opened or does not match.
          PathSpecError: if the path specification is incorrect.
        """
        if depth > self._MAXIMUM_PARENT_DEPTH:
            raise OSError("Parent image chain exceeds maximum depth.")

        location = getattr(path_spec, "location", None)
        if not location:
            raise errors.PathSpecError(
                "Unsupported path specification without location."
            )

        parent_filename = self._GetParentFilename(vmdk_handle)

        location_path_segments = file_system.SplitPath(location)
        location_path_segments.pop()
        location_path_segments.append(parent_filename)
        parent_location = file_system.JoinPath(location_path_segments)

        # Note that we don't want to set the keyword arguments when not used
        # because the path specification base class will check for unused
        # keyword arguments and raise.
        kwargs = path_spec_factory.Factory.GetProperties(path_spec)

        kwargs["location"] = parent_location
        if path_spec.parent is not None:
            kwargs["parent"] = path_spec.parent

        parent_path_spec = path_spec_factory.Factory.NewPathSpec(
            path_spec.type_indicator, **kwargs
        )

        if not file_system.FileEntryExistsByPathSpec(parent_path_spec):
            raise OSError(f"Unable to locate parent image: {parent_filename:s}.")

        parent_vmdk_handle = self._OpenVMDKHandle(file_system, parent_path_spec)
        self._parent_vmdk_handles.append(parent_vmdk_handle)

        if (
            vmdk_handle.parent_content_identifier
            != parent_vmdk_handle.content_identifier
        ):
            raise OSError(
                f"Content identifier of parent image: {parent_filename:s} does not "
                "match."
            )

        if self._HasParentImage(parent_vmdk_handle):
            self._OpenParentImage(
                file_system, parent_path_spec, parent_vmdk_handle, depth=depth + 1
            )

        vmdk_handle.set_parent(parent_vmdk_handle)

    def _OpenVMDKHandle(self, file_system, parent_path_spec):
        """Opens a VMDK handle and its extent data files.

        Args:
          file_system (FileSystem): file system of the VMDK descriptor file.
          parent_path_spec (PathSpec): path specification of the VMDK descriptor
              file.

        Returns:
          pyvmdk.handle: VMDK handle.

        Raises:
          OSError: if the extent data files could not be located.
          PathSpecError: if the path specification is incorrect.
        """
        parent_location = getattr(parent_path_spec, "location", None)
        if not parent_location:
            raise errors.PathSpecError(
                "Unsupported parent path specification without location."
            )

        # Note that we cannot use pyvmdk's open_extent_data_files_as_file_objects
        # function since it does not handle the file system abstraction dfVFS provides.

        file_object = resolver.Resolver.OpenFileObject(
            parent_path_spec, resolver_context=self._resolver_context
        )
        vmdk_handle = pyvmdk.handle()
        vmdk_handle.open_file_object(file_object)

        parent_location_path_segments = file_system.SplitPath(parent_location)

        extent_data_files = []
        for extent_descriptor in iter(vmdk_handle.extent_descriptors):
            extent_data_filename = extent_descriptor.filename

            _, path_separator, filename = extent_data_filename.rpartition("/")
            if not path_separator:
                _, path_separator, filename = extent_data_filename.rpartition("\\")

            if not path_separator:
                filename = extent_data_filename

            # The last parent location path segment contains the extent data filename.
            # Since we want to check if the next extent data file exists we remove the
            # previous one form the path segments list and add the new filename. After
            # that the path segments list can be used to create the location string.

            parent_location_path_segments.pop()
            parent_location_path_segments.append(filename)
            extent_data_file_location = file_system.JoinPath(
                parent_location_path_segments
            )
            # Note that we do not want to set the keyword arguments when not used
            # because the path specification base class will check for unused keyword
            # arguments and raise.

            kwargs = path_spec_factory.Factory.GetProperties(parent_path_spec)

            kwargs["location"] = extent_data_file_location
            if parent_path_spec.parent is not None:
                kwargs["parent"] = parent_path_spec.parent

            extent_data_file_path_spec = path_spec_factory.Factory.NewPathSpec(
                parent_path_spec.type_indicator, **kwargs
            )
            if not file_system.FileEntryExistsByPathSpec(extent_data_file_path_spec):
                if vmdk_handle.number_of_extents > 1:
                    break

                if vmdk_handle.disk_type not in (
                    pyvmdk.disk_types.MONOLITHIC_SPARSE,
                    pyvmdk.disk_types.STREAM_OPTIMIZED,
                ):
                    break

                if extent_descriptor.type != pyvmdk.extent_types.SPARSE:
                    break

                # VMDK file was likely renamed.
                extent_data_file_path_spec = parent_path_spec

            extent_data_files.append(extent_data_file_path_spec)

        if len(extent_data_files) != vmdk_handle.number_of_extents:
            vmdk_handle.close()
            raise OSError("Unable to locate all extent data files.")

        file_objects = []
        for extent_data_file_path_spec in extent_data_files:
            file_object = resolver.Resolver.OpenFileObject(
                extent_data_file_path_spec, resolver_context=self._resolver_context
            )
            file_objects.append(file_object)

        vmdk_handle.open_extent_data_files_as_file_objects(file_objects)

        return vmdk_handle

    def get_size(self):
        """Retrieves the size of the file-like object.

        Returns:
          int: size of the file-like object data.

        Raises:
          OSError: if the file-like object has not been opened.
        """
        if not self._is_open:
            raise OSError("Not opened.")

        return self._file_object.get_media_size()
