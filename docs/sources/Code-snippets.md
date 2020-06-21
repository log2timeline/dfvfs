# Code snippets

This page contains a wide range of code snippets for using dfVFS.

## Working with storage media images and devices

Assume we have a QCOW2 storage media image:

```bash
qcowmount image.qcow2 fuse/
```

Containing the following partition table:

```bash
mmls fuse/qcow1
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

     Slot    Start        End          Length       Description
00:  Meta    0000000000   0000000000   0000000001   Primary Table (#0)
01:  -----   0000000000   0000000062   0000000063   Unallocated
02:  00:00   0000000063   0016755794   0016755732   NTFS (0x07)
03:  -----   0016755795   0016777215   0000021421   Unallocated
```

### Exposing a volume as a data range

To create a file-like object of the volume stored in partition 1 (slot `00:00`).

```python
from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.resolver import resolver

location = 'image.qcow2'
range_offset = 63 * 512
range_size = 16755732 * 512

os_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_OS, location=location)
qcow_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_QCOW, parent=os_path_spec)
data_range_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_DATA_RANGE, range_offset=range_offset, range_size=range_size, parent=qcow_path_spec)

file_object = resolver.Resolver.OpenFileObject(data_range_path_spec)
```

### Traversing a file system

To retrieve a file entry of the root directory:

```python
from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.resolver import resolver

location = 'image.qcow2'

os_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_OS, location=location)
qcow_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_QCOW, parent=os_path_spec)
tsk_partition_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1', parent=qcow_path_spec)
tsk_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_TSK, location='/', parent=tsk_partition_path_spec)

file_entry = resolver.Resolver.OpenFileEntry(tsk_path_spec)
```

To iterate over the sub file entries in the root directory:

```python
for sub_file_entry in file_entry.sub_file_entries:
  print(sub_file_entry.name)
```

### Retrieving an inode value

```python
from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.resolver import resolver

image_location = 'image.E01'
file_location = '/Users/MyUser/AppData/Local/Microsoft/Office/15.0/OfficeFileCache/MyFile.txt'

os_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_OS, location=image_location)
ewf_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_EWF, parent=os_path_spec)
tsk_path_spec = factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_TSK, location=file_location, parent=ewf_path_spec)

file_entry = resolver.Resolver.OpenFileEntry(tsk_path_spec)

stat_object = file_entry.GetStat()

print('Inode: {0:d}'.format(stat_object.ino))
```
