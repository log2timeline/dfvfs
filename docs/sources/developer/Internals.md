# Introduction

dfVFS was developed to provide a generic means for
[Plaso](https://github.com/log2timeline/plaso) to access files via the
operating system and those contained in storage media image formats.

In dfVFS terminology:

* a data stream encapsulates the contents of a file, an NTFS ADS or HFS resource fork.
* a file entry encapsulates the file system metadata related to files, directories, symbolic links or equivalent file system related structures.
* a file system encapsulates the hierarchy of file entries within a single volume.
* a volume is part of a volume system and often contains a file system (e.g. NTFS) or a sub volume system (e.g. VSS).
* a volume system encapsulates one or more volumes.

dfVFS separates the concerns relating:

* addressing of file entries, such as the file path, with type specific path specification;
* file-based Input/Output (IO), with type specific basic file-like objects;
* traversing file entries and metadata, with type specific virtual file system and/or file entry;
* format detection, with a format analyzer with type specific helpers.

## The path specification

The path specification is equivalent to the path on most operating systems.
Though the actual format of the path can be operating systems specific, e.g.
Linux uses /home/myuser/myfile.txt and Windows C:\Users\MyUser\MyFile.txt.

In dfVFS the path specification is defined as a container with a *type
indicator* with zero or more *addressing attributes*. One of the more common
addressing attributes is e.g. location with for the operating system path
specification would contain the operating system specific path, e.g. on Windows
location=C:\Users\MyUser\MyFile.txt.

Path specifications can be stacked to access files in storage media images and
other container formats e.g. archive files like ZIP. For this the path
specification can define a *parent* path specification. Note that parent here
refers to the path specification and not the parent in the path segment e.g.
defined by the location addressing attribute.

Next follows a pseudo code implementation of a stacked path specification that
defines the location of C:\Users\MyUser\MyFile.txt on the first partition of
QCOW version 2 image.

```
type=OS, location=/home/myuser/myimages/image.qcow2
type=QCOW
type=TSK_PARTITION, location=/p1
type=TSK, inode=128, location=/Users/MyUser/MyFile.txt
```

Note that the parent is not explicitly defined in the example but the parent is
defined implicit by the preceding path specification. E.g. OS is the parent of
the QCOW path specification type and QCOW the parent of the TSK_PARTITION path
specification type.

Also note that though the location of the file within the Windows operating
system would be C:\Users\MyUser\MyFile.txt it is defined in the the TSK path
specification type as /Users/MyUser/MyFile.txt. dfVFS defines a *Windows path
resolver helper* to map Windows paths to a location within images.

The inode addressing attribute in the TSK path specification type is used for
faster access to the file within the TSK virtual file system implementation.

**TODO**

## The path specification resolver

The path specification resolver is used to resolve a path specification to a
file-like object or virtual file system object.

**TODO**

## The mount point manager

**TODO**

## The credentials manager

**TODO**

## Additional helpers

Besides the previously mentioned objects dfVFS also provides several [helper objects](Helpers.md).
