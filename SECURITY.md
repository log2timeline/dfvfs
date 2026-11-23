# Security Policy

## Supported versions

Security fixes are made on the `main` branch and included in the next
release. Older releases are not patched.

## Reporting a vulnerability

Please do not report security issues in public issues or pull requests.

Use GitHub private vulnerability reporting:
https://github.com/log2timeline/dfvfs/security/advisories/new

Include:

* the affected version or commit
* a description of the issue and its impact
* steps or a minimal sample file to reproduce it (do not attach real evidence)

## What to expect

* Acknowledgement within 7 days.
* An assessment and an expected fix timeline within 30 days.
* Coordinated disclosure: we ask for up to 90 days before public disclosure
  and credit reporters in the advisory unless they prefer otherwise.

## Scope

dfVFS parses untrusted disk images, file systems and archives.

In scope:

* crashes, hangs or unbounded memory or CPU use triggered by crafted input
* access outside the intended file system or mount point (path traversal)
* incorrect results that let crafted input hide or alter evidence

Out of scope:

* bugs in native libyal libraries, which should be reported to the libyal project
* issues that require a malicious local user or modified project code
* performance problems with non-adversarial input

## Using the library safely

Treat all evidence as untrusted: run processing in a sandbox with CPU, memory
and time limits, and without credentials or network access.
