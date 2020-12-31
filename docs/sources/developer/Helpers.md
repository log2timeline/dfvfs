# Helpers

dfVFS currently provides the following helper objects:

* Data slice interface for file-like objects
* Fake file system builder
* Source scanner
* Volume scanner
* File system searcher
* Windows path resolver helper

## Data slice interface for file-like objects

The data slice interface for file-like objects provides a wrapper for dfVFS
FileIO objects, so that they can be interacted with as data slices. The data
slice interface is for example used in [Plaso's PE parser](https://github.com/log2timeline/plaso/blob/62d4fa7d25e793dba0557e12c5d61c6052a4a7a4/plaso/parsers/pe.py#L194).

To create a data slice from a file-like object.

```python
from dfvfs.helpers import data_slice

...
slice_object = DataSlice(file_object)
```

To use:

```python
signature = slice_object[0:4]
```

## Fake file system builder

The fake file system builder is intended for testing purposes. It provides
helper functions that take care of setting up a dfVFS fake file system.

To create a fake file system with a single file `/testfile`.

```python
from dfvfs.helpers import fake_file_system_builder

file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()
file_system_builder.AddFile('/testfile', b'data')
```

## Source scanner

The source scanner was originally created for [Plaso](https://github.com/log2timeline/plaso/blob/993ab0111bbf594c9b6d679415c80f8409cad0b5/plaso/cli/storage_media_tool.py#L93)
tools that deal with storage media devices and images. However it is also
used by the dfVFS volume scanner.

The source scanner can be used to analyze source (or input) data, which for
Plaso can be an individual file, a directory or a storage media device or
image.

The source scanner tries to determine what input we are dealing with:

* a file that contains a storage media image;
* a device file of a storage media image device;
* a regular file or directory.

The source scanner scans for different types of elements:

* supported types of storage media images;
* supported types of volume systems;
* supported types of file systems.

These elements are represented as source scan nodes.

The source scanner uses the source scanner context to keep track of
the nodea and user provided context information, such as:

* which partition to default to;
* which VSS stores to default to.

An example of how to use the source scanner can be found in the [source analyzer](https://github.com/open-source-dfir/dfvfs-snippets/blob/main/scripts/source_analyzer.py)
script.

## Volume scanner

The volume scanner is an extension of the source analyzer that looks for
volumes that contain dfVFS supported volume and file systems. It is intended
to help with programmatically handled various types of volume and file systems
so the application that uses it can focus on reading file it is interested in.

**TODO: add more information about VolumeScannerMediator and VolumeScannerOptions**

Examples of how to use the volume scanner can be found in the [list file entries](https://github.com/open-source-dfir/dfvfs-snippets/blob/main/scripts/list_file_entries.py)
and the [recursive hasher](https://github.com/open-source-dfir/dfvfs-snippets/blob/main/scripts/recursive_hasher.py)
scripts.

### Windows volume scanner

The Windows volume scanner is a variant of the volume scanner that looks for
volumes that contain an installation of the Windows operating system.

An example of how to use the source scanner can be found in the [WinReg-KB](https://github.com/libyal/winreg-kb/blob/2e285132b70ce036b7492921ad29f9caf663492e/winregrc/collector.py#L58).

## File system searcher

The file system searcher was originally created for event extraction with
[collection filters](https://plaso.readthedocs.io/en/latest/sources/user/Collection-Filters.html)
in [Plaso](https://github.com/log2timeline/plaso/blob/993ab0111bbf594c9b6d679415c80f8409cad0b5/plaso/cli/storage_media_tool.py#L93).

**TODO: add more information about FindSpec**

**TODO: add example**

## Windows path resolver helper

The Windows path resolver helper can be used to resolve various forms Windows
paths, e.g. below are several forms of path definitions found in the Windows
Registry:

| **Description** | **Example** |
| --- | --- |
| Volume 'absolute' path | `C:\Windows\System32\icardres.dll` |
| Local 'absolute' path | `\Windows\System32\Drivers\acpiex.sys` |
| Local 'relative' path | `System32\Drivers\acpiex.sys` |
| Path with environment variable | `%systemroot%\system32\svchost.exe` |
| Short name volume 'absolute' path | `C:\PROGRA~1\COMMON~1\MICROS~1\DW\DW20.EXE` |
| | `\SystemRoot\System32\drivers\1394ohci.sys` |
| | `$(runtime.system32)\winhttp.dll` |
| | `\??\C:\WINDOWS\Microsoft.NET\Framework\v1.1.4322\ngen.exe` |
| | `SYSVOL\Windows\System32\wbem\WmiPrvSE.exe` |

The Windows path resolver helper can be found in:

```
dfvfs/helpers/windows_path_resolver.py
```

**TODO: add example**

### Notes

**TODO add more description here**

| **Description** | **Example** |
| --- | --- |
| Device path | `\\.\PhysicalDrive0` |
| Volume device path | `\\.\C:` |
| Volume file system path | `\\.\C:\` |
| Volume path | `\DEVICE\HARDDISKVOLUME2` |
| Extended-length path | `\\?\C:\directory\file.txt` |
| Extended-length UNC path | `\\?\UNC\server\share\directory\file.txt` |
| Local 'absolute' path | `\directory\file.txt` <br> `\directory\\file.txt` |
| Local 'relative' path | `directory\file.txt` <br> `..\directory\file.txt` <br> `.\directory\file.txt` |
| Volume 'absolute' path | `C:\directory\file.txt` |
| Volume 'relative' path | `C:directory\file.txt` |
| UNC path | `\\server\share\directory\file.txt` |
| Path with environment variable | `%SystemRoot%\file.txt` |
| Path with trailing number to indicate the corresponding TYPELIB resource inside the PE/COFF | `C:\WINDOWS\PCHealth\HelpCtr\Binaries\HelpCtr.exe\1` |
| Path with volume creation time (FILETIME) and (volume) serial number (found in SuperFetch database and Prefetch files) | `\VOLUME{01d15f816d07ba5e-5e6d77ca}\Windows\System32`

