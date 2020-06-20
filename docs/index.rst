Welcome to the dfVFS documentation
=======================================

dfVFS, or Digital Forensics Virtual File System, provides read-only access to
file-system objects from various storage media types and file formats. The goal
of dfVFS is to provide a generic interface for accessing file-system objects,
for which it uses several back-ends that provide the actual implementation of
the various storage media types, volume systems and file systems.

dfVFS originates from the `Plaso project <https://github.com/log2timeline/plaso>`__
and is also based on ideas from the `GRR project <https://github.com/google/grr>`__.
It was largely rewritten and made into a stand-alone project to provide more
flexibility and allow other projects to make use of the VFS functionality.
dfVFS originally was named PyVFS, but that name conflicted with another project.

The source code is available from the `project page <https://github.com/log2timeline/dfvfs>`__.

.. toctree::
   :maxdepth: 2

   sources/user/index

.. toctree::
   :maxdepth: 2

   Code snippets <sources/Code-snippets>

.. toctree::
   :maxdepth: 2

   Path specifications <sources/Path-specifications>

.. toctree::
   :maxdepth: 2

   sources/developer/index

.. toctree::
   :maxdepth: 2

   Supported formats <sources/Supported-formats>

.. toctree::
   :maxdepth: 2

   API documentation <sources/api/dfvfs>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

