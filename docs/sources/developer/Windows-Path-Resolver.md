# Windows path resolver

dfVFS provides a Windows path resolver helper to resolve various forms Windows
uses to define paths, e.g. below are several forms of path definitions found in
the Windows Registry:

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
