# Path specifications

## Terminology

In dfVFS a path specification is defines the location of a file system entry
or data stream. It is comparable with the path on an operating system with the
diffence that the dfVFS path specification includes information about its
parents, such a the volume system of the file system.

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
version 20200625.

| **Type indicator** | **Description** |
| --- | --- |
| TYPE_INDICATOR_APFS | The Apple File System (APFS) type |
| TYPE_INDICATOR_APFS_CONTAINER | The Apple File System (APFS) container volume system type |
| TYPE_INDICATOR_BDE | The BitLocker Drive Entryption (BDE) volume system type |
| TYPE_INDICATOR_COMPRESSED_STREAM | The compressed stream type |
| TYPE_INDICATOR_CPIO | The cpio archive file type |
| TYPE_INDICATOR_DATA_RANGE | The data range type |
| TYPE_INDICATOR_ENCODED_STREAM | The encoded stream type |
| TYPE_INDICATOR_ENCRYPTED_STREAM | The encrypted stream type |
| TYPE_INDICATOR_EWF | The EWF storage media image type |
| TYPE_INDICATOR_EXT | The Extended file system (ext) type |
| TYPE_INDICATOR_FAKE | The fake file system type |
| TYPE_INDICATOR_FVDE | The FileVault Drive Enryption (FVDE) volume system type |
| TYPE_INDICATOR_GZIP | The gzip compressed file type |
| TYPE_INDICATOR_LUKSDE | The LUKS drive encryption volume system type |
| TYPE_INDICATOR_LVM | The Logical Volume Manager (LVM) volume system type |
| TYPE_INDICATOR_MOUNT | Type to represent a mount point |
| TYPE_INDICATOR_NTFS | The Windows NT file system (NTFS) type |
| TYPE_INDICATOR_OS | The operating system type |
| TYPE_INDICATOR_QCOW | The QCOW storage media image type |
| TYPE_INDICATOR_RAW | The RAW storage media image type |
| TYPE_INDICATOR_SQLITE_BLOB | The SQLite binary large objects (BLOB) type |
| TYPE_INDICATOR_TAR | The tar archive file type |
| TYPE_INDICATOR_TSK | The SleuthKit file system type |
| TYPE_INDICATOR_TSK_PARTITION | The SleuthKit partition volume system type |
| TYPE_INDICATOR_VHDI | The VHD storage media image type |
| TYPE_INDICATOR_VMDK | The VMDK storage media image type |
| TYPE_INDICATOR_VSHADOW | The VSS volume system type |
| TYPE_INDICATOR_ZIP | The zip archive file type |

## Addressing attributes

All types, with the exception of the operating system type, require a parent
path specification addressing attribute.

### The APFS file system type

The APFS type (TYPE_INDICATOR_APFS) is a type that addresses files stored within
an Apple file system (APFS).

| **Attribute name** | **Description** |
| --- | --- |
| identifier | The identifier of the file entry within the file system. Comparable to the catalog node identifier (CNID) on HFS. |
| location | The location of the file entry |
| parent | The parent path specification |

### The APFS container volume system type

The APFS container type (TYPE_INDICATOR_APFS_CONTAINER) is a type that addresses
volumes stored within a Apple file system (APFS) container.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the volume within the container |
| parent | The parent path specification |
| volume_index | The index of the volume within the container |

### The BDE volume system type

The BDE type (TYPE_INDICATOR_BDE) is a type that addresses volumes stored
within a BitLocker encrypted volume.

| **Attribute name** | **Description** |
| --- | --- |
| password | The password to unlock the BitLocker volume |
| parent | The parent path specification |
| recovery_password | The recovery password to unlock the BitLocker volume |
| startup_key | The name of the startup key file to unlock the BitLocker volume |

**Note that it is recommended to use the credential manager instead of providing
decryption keys (credentials) in a path specification.**

### The compressed stream type

The compressed stream type (TYPE_INDICATOR_COMPRESSED_STREAM) is an internal
type that defines the following addressing attributes:

| **Attribute name** | **Description** |
| --- | --- |
| compression_method | The method used to compress the stream |
| parent | The parent path specification |

### The cpio archive file type

The cpio type (TYPE_INDICATOR_CPIO) is a type that addresses files stored within
the cpio archive file format.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry within the cpio archive |
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

### The encrypted stream type

The encrypted stream type (TYPE_INDICATOR_ENCRYPTED_STREAM) is an internal type
that defines the following addressing attributes:

| **Attribute name** | **Description** |
| --- | --- |
| cipher_mode | The cipher mode used by the encryption method, for example XTS  |
| encryption_method | The method used to encrypt the stream, for example AES |
| initialization_vector | The initialization vector used to encrypt the stream |
| key | The key used to encrypt the stream |
| parent | The parent path specification |

**Note that it is recommended to use the credential manager instead of providing
decryption keys (credentials) in a path specification.**

### The EWF storage media image type

The EWF type (TYPE_INDICATOR_EWF) is a type that addresses storage media images
stored within the [Expert Witness (Compression) Format](https://forensicswiki.xyz/wiki/index.php?title=Encase_image_file_format).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

**Note that at the moment this type is not addressable as a file system.**

**Note that at the moment L01 or Lx01 files are not supported.**

### The EXT file system type

The EXT type (TYPE_INDICATOR_EXT) is a type that addresses files stored within
a Extended file system (ext).

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry |
| inode | The inode number of the file entry |

### The fake file system type

The FAKE type (TYPE_INDICATOR_FAKE) is a virtual file system intended for
testing purposes.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the file entry |
| parent | The parent path specification, must be None |

### The FVDE volume system type

The FVDE type (TYPE_INDICATOR_FVDE) is a type that addresses volumes stored
within a FileVault encrypted CoreStorage volume.

| **Attribute name** | **Description** |
| --- | --- |
| encrypted_root_plist | The path of the EncryptedRoot.plist.wipekey file to unlock the FileVault volume |
| password | The password to unlock the FileVault volume |
| parent | The parent path specification |
| recovery_password | The recovery password to unlock the FileVault volume |

**Note that it is recommended to use the credential manager instead of providing
decryption keys (credentials) in a path specification.**

### The gzip file type

The GZIP type (TYPE_INDICATOR_GZIP) is a type that addresses data stored within
the [gzip compressed stream file format](https://forensicswiki.xyz/wiki/index.php?title=Gzip).

| **Attribute name** | **Description** |
| --- | --- |
| parent | The parent path specification |

### The LUKSDE volume system type

The LUKSDE type (TYPE_INDICATOR_LUKSDE) is a type that addresses volumes stored
within a LUKS encrypted volume.

| **Attribute name** | **Description** |
| --- | --- |
| password | The password to unlock the FileVault volume |
| parent | The parent path specification |

### The LVM volume system type

The LVM type (TYPE_INDICATOR_LVM) is a type that addresses volumes stored
within a Logical Volume Manager (LVM) volume system.

| **Attribute name** | **Description** |
| --- | --- |
| location | The location of the volume within the LVM volume system |
| parent | The parent path specification |
| volume_index | The index of the volume within the LVM volume system |

### The mount type

The MOUNT type (TYPE_INDICATOR_MOUNT) is a type that defines a mount point
within dfVFS. Also see [the mount point manager](developer/Internals.md).

| **Attribute name** | **Description** |
| --- | --- |
| identifier | The identifier of the mount point |
| parent | The parent path specification, must be None |

### The NTFS file system type

The NTFS type (TYPE_INDICATOR_NTFS) is a type that addresses files stored within
a Windows NT file system (NTFS).

| **Attribute name** | **Description** |
| --- | --- |
| data_stream | The name of the data stream in the file entry |
| location | The location of the file entry |
| mft_attribute | The index of the $FILE_NAME of the MFT attribute within the MFT entry that contains the name of the file entry |
| mft_entry | The identifier of the MFT entry within the file system |
| parent | The parent path specification |

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

### The SQlite blob file type

The SQlite blob type (TYPE_INDICATOR_SQLITE_BLOB) is a type that addresses files
stored within a blob within a SQLite file.

| **Attribute name** | **Description** |
| --- | --- |
| column_name | The name of the column in which the blob is stored |
| parent | The parent path specification |
| row_condition | A condition that matches the row in which the blob is stored |
| row_index | The index of the row in which the blob is stored |
| table_name | The name of the table in which the blob is stored |

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
| inode | The inode number of the file entry |
| location | The location of the file entry |
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
