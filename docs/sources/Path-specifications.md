# Path specifications

## Terminology

### System-level path specification

A "system-level path specification" is a path specification that can be
resolved by the operating system; typically TYPE_INDICATOR_OS or equivalent.

## Type indicators

The dfVFS path specification type indicators are defined in:

```
dfvfs/lib/definitions.py
```

In your code use the type indicator as defined by dfVFS and not its value, in
case it changes. The following is a list of type indicators as available in
version 20140126.

| **Type indicator** | **Description** |
| --- | --- |
| TYPE_INDICATOR_BDE | The BDE volume system type |
| TYPE_INDICATOR_COMPRESSED_STREAM | The compressed stream type |
| TYPE_INDICATOR_DATA_RANGE | The data range type |
| TYPE_INDICATOR_ENCODED_STREAM | The encoded stream type |
| TYPE_INDICATOR_EWF | The EWF storage media image type |
| TYPE_INDICATOR_FAKE | The fake file system type |
| TYPE_INDICATOR_GZIP | The gzip file type |
| TYPE_INDICATOR_MOUNT | The mount type |
| TYPE_INDICATOR_OS | The operating system type |
| TYPE_INDICATOR_QCOW | The QCOW storage media image type |
| TYPE_INDICATOR_RAW | The RAW storage media image type |
| TYPE_INDICATOR_TAR | The tar archive file type |
| TYPE_INDICATOR_TSK | The SleuthKit file system type |
| TYPE_INDICATOR_TSK_PARTITION | The SleuthKit volume system type |
| TYPE_INDICATOR_VHDI | The VHD storage media image type |
| TYPE_INDICATOR_VMDK | The VMDK storage media image type |
| TYPE_INDICATOR_VSHADOW | The VSS volume system type |
| TYPE_INDICATOR_ZIP | The zip archive file type |

## Addressing attributes

All types, with the exception of the operating system type, require a parent
path specification addressing attribute.

### The BDE volume system type

The BDE type (TYPE_INDICATOR_BDE) is a type that addresses volumes stored
within the [BitLocker Drive Encryption](https://forensicswiki.xyz/wiki/index.php?title=BitLocker_Disk_Encryption).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that to unlock a BitLocker volume without a clear key you'll need to set the corresponding credential in the dfVFS resolver key chain.**

### The compressed stream type

The compressed stream type (TYPE_INDICATOR_COMPRESSED_STREAM) is an internal
type that defines the following addressing attributes:

| **Attribute name** | **Description** |
| --- | --- |
| compression_method | The method used to compress the stream |
| parent | The parent path specification |

### The data range type

The data range type (TYPE_INDICATOR_DATA_RANGE) is an internal type that
defines the following addressing attributes:

| **Attribute name** | **Description** |
| --- | --- |
| range_offset | The offset, in bytes, relative to the start of the parent file entry, where the data range starts |
| range_size | The size, in bytes, of the data range |
| parent | The parent path specification |


### The encoded stream type

The encoded stream type (TYPE_INDICATOR_ENCODED_STREAM) is an internal type
that defines the following addressing attributes:

| **Attribute name** | **Description** |
| --- | --- |
| encoding_method | The method used to encode the stream |
| parent | The parent path specification |

### The EWF storage media image type

The EWF type (TYPE_INDICATOR_EWF) is a type that addresses storage media images
stored within the [Expert Witness (Compression) Format](https://forensicswiki.xyz/wiki/index.php?title=Encase_image_file_format).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

**Note that at the moment L01 or Lx01 files are not supported.**

### The fake file system type

The FAKE type (TYPE_INDICATOR_FAKE) is a virtual file system intended for
testing purposes.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry |
| parent | The parent path specification, must be None |

### The gzip file type

The GZIP type (TYPE_INDICATOR_GZIP) is a type that addresses data stored within
the [gzip compressed stream file format](https://forensicswiki.xyz/wiki/index.php?title=Gzip).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

### The mount type

The MOUNT type (TYPE_INDICATOR_MOUNT) is a type that defines a mount point
within dfVFS. Also see [the mount point manager](https://github.com/log2timeline/dfvfs/wiki/Internals).

| **Attribute name** | **Description** |
| --- | --- |
| identifier | The identifier of the mount point |
| parent | The parent path specification, must be None |

### The operating system type

The OS type (TYPE_INDICATOR_OS) is a type that addresses files stored within an
operating system.

| **Attribute name** | **Description** |
| --- | --- |
| location | The operating system specific location of the file entry which corresponds to the path. <br> E.g. C:\Windows\System32\config\SAM or /etc/passwd |
| parent | The parent path specification, must be None |

### The QCOW storage media image type

The QCOW type (TYPE_INDICATOR_QCOW) is a type that addresses storage media
images stored within the [QCOW image format](https://forensicswiki.xyz/wiki/index.php?title=QCOW_Image_Format),
version 1, 2 and 3.

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

### The RAW storage media image type

The RAW storage media image type (TYPE_INDICATOR_RAW) is a type that addresses
storage media images stored within the [RAW image format](https://forensicswiki.xyz/wiki/index.php?title=Raw_Image_Format).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

### The tar archive file type

The TAR type (TYPE_INDICATOR_TAR) is a type that addresses files stored within
the [tar archive file format](https://forensicswiki.xyz/wiki/index.php?title=Tar).

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry within the tar archive |
| parent | The parent path specification |

**Note that to access e.g. a .tar.gz the a path specification of type TAR should be stacked on top of one of type GZIP.**

### The SleuthKit file system type

The TSK type (TYPE_INDICATOR_TSK) is a type that addresses files stored within
a SleuthKit supported file system.

| **Attribute name** | **Description** |
| --- | --- |
| inode | The inode of the file entry within the file system |
| location | The location of the file entry within the file system |
| parent | The parent path specification |

### The SleuthKit volume system type

The TSK_PARTITION type (TYPE_INDICATOR_TSK_PARTITION) is a type that addresses
volumes stored within a SleuthKit supported volume system, which largely
consists of support for the [APM](https://forensicswiki.xyz/wiki/index.php?title=APM),
[GPT](https://forensicswiki.xyz/wiki/index.php?title=GPT) and
[MBR](https://forensicswiki.xyz/wiki/index.php?title=Master_boot_record) partitioning
systems.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the volume within the volume system |
| parent | The parent path specification |
| part_index | The SleuthKit part index that indicates the volume within the volume system |
| start_offset | The start offset, in bytes, of the volume within the volume system |

### The VHD storage media image type

The VHDI type (TYPE_INDICATOR_VHDI) is a type that addresses storage media
images stored within the [Virtual Hard Disk Image format](https://forensicswiki.xyz/wiki/index.php?title=Virtual_Hard_Disk_(VHD)).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

### The VMDK storage media image type

The VMDK type (TYPE_INDICATOR_VMDK) is a type that addresses storage media
images stored within the [VMWare Virtual Disk Format](https://forensicswiki.xyz/wiki/index.php?title=VMWare_Virtual_Disk_Format_(VMDK)).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

### The VSS volume system type

The VSHADOW type (TYPE_INDICATOR_VSHADOW) is a type that addresses volumes
stored within the [Volume Shadow Snapshots (VSS)](https://forensicswiki.xyz/wiki/index.php?title=Windows_Shadow_Volumes).

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the volume within the volume system |
| parent | The parent path specification |
| store_index | The store index of the volume within the volume system |

### The zip archive file type

The ZIP type (TYPE_INDICATOR_ZIP) is a type that addresses files stored within
the [zip archive file format](https://forensicswiki.xyz/wiki/index.php?title=Zip).

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry within the zip archive |
| parent | The parent path specification |
