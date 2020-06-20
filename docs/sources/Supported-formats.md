## Supported Formats

The information below is based of version 20181124

### Storage media types

* EWF (EWF-E01, EWF-Ex01, EWF-S01) (Requires: [libewf/pyewf](https://github.com/libyal/libewf))
* QCOW version 1, 2, 3 (Requires: [libqcow/pyqcow](https://github.com/libyal/libqcow))
  * currently no differential image support
* Storage Media device (Requires: [libsmdev/pysmdev](https://github.com/libyal/libsmdev))
* (split) Storage Media RAW (Requires: [libsmraw/pysmraw](https://github.com/libyal/libsmraw))
* VHD (Requires: [libvhdi/pyvhdi](https://github.com/libyal/libvhdi))
  * differential image support as of dfVFS 20160428
* VMDK (Requires: [libvmdk/pyvmdk](https://github.com/libyal/libvmdk))
  * currently no differential image support

### Volume systems

* Apple Partition Map (APM) (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* Apple File System (APFS) container version 2 (Requires: [libfsapfs/pyfsapfs](https://github.com/libyal/libfsapfs))
  * as of dfVFS 20181124
* BitLocker Disk Encryption (BDE) (Requires: [libbde/pybde](https://github.com/libyal/libbde))
  * AES-XTS variant not supported yet
* FileVault Disk Encryption (FVDE) (or FileVault 2) (Requires: [libfvde/pyfvde](https://github.com/libyal/libfvde))
* GPT (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* LVM (Requires: [libvslvm/pyvslvm](https://github.com/libyal/libvslvm))
  * At the moment only single physical volume LVM support
* MBR (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* Volume Shadow Snapshots (VSS) (Requires: [libvshadow/pyvshadow](https://github.com/libyal/libvshadow))

### File systems

* Apple File System (APFS) version 2 (Requires: [libfsapfs/pyfsapfs](https://github.com/libyal/libfsapfs))
  * as of dfVFS 20181124
* ext version 2, 3, 4 (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* FAT (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* HFS, HFS+, HFSX (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* NTFS version 3 (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk) or [libfsntfs/pyfsntfs](https://github.com/libyal/libfsntfs))
* UFS version 1, 2 (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))

**TODO add more detail here regarding FAT and other supported FS**

### Compressed stream file types

* bzip2
* gzip
* lzma
* xz
* zlib (both zlib-DEFLATE and raw-DEFLATE)

### Encoded stream file types

* base16
* base32
* base64

### Encrypted stream file types

* AES-CBC, AES-CFB, AES-ECB, AES-OFB (Requires: [pycrypto](https://www.dlitz.net/software/pycrypto/))
* Blowfish (Requires: [pycrypto](https://www.dlitz.net/software/pycrypto/))
* DES3 (Requires: [pycrypto](https://www.dlitz.net/software/pycrypto/))
* RC4 (Requires: [pycrypto](https://www.dlitz.net/software/pycrypto/))

### Archive file types

* cpio
* tar
* zip

### Other file types

* blob stored in SQlite
