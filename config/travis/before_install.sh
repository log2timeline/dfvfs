#!/bin/bash
#
# Script to set up Travis-CI test VM.

COVERALL_DEPENDENCIES="python-coverage python-coveralls python-docopt";

PYTHON2_DEPENDENCIES="libbde-python libewf-python libfsntfs-python libfwnt-python libqcow-python libsigscan-python libsmdev-python libsmraw-python libvhdi-python libvmdk-python libvshadow-python libvslvm-python python-construct python-crypto python-dfdatetime python-lzma python-pytsk3 python-six";

PYTHON3_DEPENDENCIES="libbde-python3 libewf-python3 libfsntfs-python3 libfwnt-python3 libqcow-python3 libsigscan-python3 libsmdev-python3 libsmraw-python3 libvhdi-python3 libvmdk-python3 libvshadow-python3 libvslvm-python3 python3-construct python3-crypto python3-dfdatetime python3-pytsk3 python3-six";

# Exit on error.
set -e;

if test `uname -s` = "Darwin";
then
	git clone https://github.com/log2timeline/l2tdevtools.git;

	mv l2tdevtools ../;
	mkdir dependencies;

	PYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py --download-directory=dependencies --preset=dfvfs;

elif test `uname -s` = "Linux";
then
	sudo add-apt-repository ppa:gift/dev -y;
	sudo apt-get update -q;
	sudo apt-get install -y ${COVERALL_DEPENDENCIES} ${PYTHON2_DEPENDENCIES} ${PYTHON3_DEPENDENCIES};
fi
