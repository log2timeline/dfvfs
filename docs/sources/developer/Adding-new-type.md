# Adding a new VFS type

Multiple steps are involved in adding a new dfVFS type:

1. Adding a type indicator
2. Adding a path specification
3. Adding a virtual file system and file entry implementation
4. Adding a file IO implementation
5. Adding a path specification resolver helper
6. Adding a format analyzer helper

## Adding a type indicator

The type indicators are stored in:

```
dfvfs/lib/definitions.py
```

Add a new type indicator:

```
TYPE_INDICATOR_MY = 'MY'
```

## Adding a path specification

The path specifications are stored in:

```
dfvfs/path/
```

Create a new path specification:

```
dfvfs/path/my_path_specification.py
```

Implement a path specification class based on the PathSpec interface class:

```
from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec

class MyPathSpec(path_spec.PathSpec):
  """Class that implements the my path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

A path specification class largely consists of:

* an object initialization method (``` __init__ ```) that sets the class attributes;
* a ``` comparable ``` property that returns a comparable string form of the path specification.

The comparable string form normally consist of multiple (newline terminated)
lines in the form:

```
type: TYPE_INDICATOR, ADDRESSING_ATTRIBUTES
```

where every line represent an individual path specification.

Make sure the path specification will register with the factory on import.

```
factory.Factory.RegisterPathSpec(MyPathSpec)
```

To have the path specification loaded when dfvfs is used, make sure to include
in:

```
dfvfs/path/__init__.py
```

```
from dfvfs.path import my_path_specification
```

## Adding a virtual file system and file entry implementation

The virtual file systems and file entries are stored in:

```
dfvfs/vfs/
```

The file system and file entry are co-dependent.

### Adding a virtual file system implementation

Create a new file system and file entry:

```
dfvfs/path/my_file_system.py
```

Implement a file system class based on the FileSystem interface class:

```
from dfvfs.lib import definitions
from dfvfs.path import my_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import my_file_entry

class MyFileSystem(file_system.FileSystem):
  """Class that implements my file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

A file system class largely consists of:

* A class constant to define the path (segment) separator used by the file system (``` PATH_SEPARATOR ```);
* A method to determine if a file entry for a specific path specification exists (``` FileEntryExistsByPathSpec ```);
* A method to retrieve if a file entry for a specific path specification (``` GetFileEntryByPathSpec ```);
* A method to retrieve the root file entry (``` GetRootFileEntry ```).

### Adding a virtual file entry implementation

Create a new file system and file entry:

```
dfvfs/path/my_file_entry.py
```

Implement a file entry class based on the FileEntry interface class and a
directory class based on the Directory interface class:

```
from dfvfs.lib import definitions
from dfvfs.file_io import fake_file_io
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_entry

class MyDirectory(file_entry.Directory):
  """Class that implements my directory object."""
  ...

class MyFileEntry(file_entry.FileEntry):
  """Class that implements my file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

A directory class largely consists of:

* A protected method to generate path specification of directory entries for a specific directory path specification (``` _EntriesGenerator ```).

A file entry class largely consists of:

* (``` _GetDirectory ```);
* (``` _GetStat ```);
* a ``` name ``` property that ...
* a ``` sub_file_entries ``` property that ...
* (``` GetFileObject ```);
* (``` GetParentFileEntry ```).

**TODO describe a bit more what should be in the class.**

## Adding a file IO implementation

The file IO (or file-like) objects are stored in:

```
dfvfs/file_io/
```

Create a new file IO object:

```
dfvfs/file_io/my_file_io.py
```

Implement a path specification class based on the FileIO interface class:

```
class MyFile(file_io.FileIO):
  """Class that implements my file-like object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

A file IO class largely consists of:

* (``` open ```);
* (``` close ```);
* (``` read ```);
* (``` seek ```);
* (``` get_offset ```);
* (``` get_size ```);

**TODO describe a bit more what should be in the class.**

dfVFS does not implement ``` write ``` or any of the ``` readline ``` functions
in its file-like object. Also ``` tell ``` is implemented in the FileIO
interface as an alias of ``` get_offset ```.

## Adding a path specification resolver helper

The path specification resolver helpers are stored in:

```
dfvfs/resolver/
```

Create a new resolver helper:

```
dfvfs/resolver/my_resolver_helper.py
```

Implement a resolver helper class based on the ResolverHelper interface class:

```
from dfvfs.lib import definitions
from dfvfs.resolver import resolver_helper

class MyResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements my resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

A resolver helper class largely consists of:

* (``` NewFileObject ```);
* (``` NewFileSystem ```).

**TODO describe a bit more what should be in the class.**

Make sure the resolver helper will register with the resolver on import.

```
resolver.Resolver.RegisterHelper(MyResolverHelper())
```

To have the resolver helper loaded when the resolver is used, make sure to include in:

```
dfvfs/resolver/__init__.py
```

```
from dfvfs.resolver import my_resolver_helper
```

## Adding a format analyzer helper

The format analyzer helpers are stored in:

```
dfvfs/analyzer/
```

Create a new analyzer helper:

```
dfvfs/analyzer/my_analyzer_helper.py
```

Implement an analyzer helper class based on the AnalyzerHelper interface class:

```
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions

class MyAnalyzerHelper(resolver_helper.AnalyzerHelper):
  """Class that implements my analyzer helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MY
  ...
```

An analyzer helper class largely consists of:

* A FORMAT_CATEGORIES definition;
* (``` GetFormatSpecification ```)

**TODO describe a bit more what should be in the class.**

Make sure the analyzer helper will register with the analyzer on import.

```
analyzer.Analyzer.RegisterHelper(MyAnalyzerHelper())
```

To have the analyzer helper loaded when the analyzer is used, make sure to include in:

```
dfvfs/analyzer/__init__.py
```

```
from dfvfs.analyzer import my_analyzer_helper
```
