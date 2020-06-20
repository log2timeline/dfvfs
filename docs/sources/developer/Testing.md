# Testing

## Unit tests

dfVFS comes with unit tests tests. These tests are stored in the `tests`
subdirectory.

To run the unit tests:

```bash
PYTHONPATH=. python run_tests.py
```

Or on Windows:

```bash
set PYTHONPATH=.
C:\Python38\python.exe run_tests.py
```

If you're running git on Windows make sure you have autocrlf turned off
otherwise the tests using the test text files will fail.

```bash
git config --global core.autocrlf false
```
