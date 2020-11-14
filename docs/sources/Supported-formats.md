## Supported Formats

The information below is based of version 20200920

### Storage media types

* EWF (EWF-E01, EWF-Ex01, EWF-S01) (Requires: [libewf/pyewf](https://github.com/libyal/libewf))
* QCOW version 1, 2, 3 (Requires: [libqcow/pyqcow](https://github.com/libyal/libqcow))
  * currently no differential image support
* Storage Media device (Requires: [libsmdev/pysmdev](https://github.com/libyal/libsmdev))
* (split) Storage Media RAW (Requires: [libsmraw/pysmraw](https://github.com/libyal/libsmraw))
* VHD and VHDX (Requires: [libvhdi/pyvhdi](https://github.com/libyal/libvhdi))
* VMDK (Requires: [libvmdk/pyvmdk](https://github.com/libyal/libvmdk))
  * currently no differential image support

### Volume systems

* Apple Partition Map (APM) (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* Apple File System (APFS) container version 2 (Requires: [libfsapfs/pyfsapfs](https://github.com/libyal/libfsapfs))
* BitLocker Disk Encryption (BDE) (Requires: [libbde/pybde](https://github.com/libyal/libbde))
* FileVault Disk Encryption (FVDE) (or FileVault 2) (Requires: [libfvde/pyfvde](https://github.com/libyal/libfvde))
* GPT (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* LVM (Requires: [libvslvm/pyvslvm](https://github.com/libyal/libvslvm))
  * At the moment only single physical volume LVM support
* MBR (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* Volume Shadow Snapshots (VSS) (Requires: [libvshadow/pyvshadow](https://github.com/libyal/libvshadow))

### File systems

* Apple File System (APFS) version 2 (Requires: [libfsapfs/pyfsapfs](https://github.com/libyal/libfsapfs))
* ext version 2, 3, 4 (Requires: [libfsext/pyfsext](https://github.com/libyal/libfsext) or [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* FAT (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* traditional HFS (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* HFS+, HFSX (Requires: [libfshfs/pyfshfs](https://github.com/libyal/libfshfs) or Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* NTFS version 3 (Requires: [libfsntfs/pyfsntfs](https://github.com/libyal/libfsntfs) or [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* UFS version 1, 2 (Requires: [libtsk](https://github.com/sleuthkit/sleuthkit/)/[pytsk](https://github.com/py4n6/pytsk))
* XFS version 4, 5 (Requires: [libfsxfs/pyfsxfs](https://github.com/libyal/libfsxfs))

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

* AES-CBC, AES-CFB, AES-ECB, AES-OFB (Requires: [Cryptography.io](https://cryptography.io/en/latest/))
* Blowfish (Requires: [Cryptography.io](https://cryptography.io/en/latest/))
* DES3 (Requires: [Cryptography.io](https://cryptography.io/en/latest/))
* RC4 (Requires: [Cryptography.io](https://cryptography.io/en/latest/))

### Archive file types

* cpio
* tar
* zip

### Other file types

* blob stored in SQlite
