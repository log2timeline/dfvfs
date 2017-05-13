#!/bin/bash
#
# Script to set up Travis-CI test VM.

COVERALL_DEPENDENCIES="python-coverage python-coveralls python-docopt";

L2TBINARIES_DEPENDENCIES="construct dfdatetime libbde libewf libfsntfs libfvde libfwnt libqcow libsigscan libsmdev libsmraw libvhdi libvmdk libvshadow libvslvm lzma pycrypto pysqlite pytsk3 six";

L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr";

PYTHON2_DEPENDENCIES="libbde-python libewf-python libfsntfs-python libfvde-python libfwnt-python libqcow-python libsigscan-python libsmdev-python libsmraw-python libvhdi-python libvmdk-python libvshadow-python libvslvm-python python-backports.lzma python-construct python-crypto python-dfdatetime python-pysqlite python-pytsk3 python-six";

PYTHON2_TEST_DEPENDENCIES="python-mock";

PYTHON3_DEPENDENCIES="libbde-python3 libewf-python3 libfsntfs-python3 libfvde-python3 libfwnt-python3 libqcow-python3 libsigscan-python3 libsmdev-python3 libsmraw-python3 libvhdi-python3 libvmdk-python3 libvshadow-python3 libvslvm-python3 python3-construct python3-crypto python3-dfdatetime python3-pytsk3 python3-six";

PYTHON3_TEST_DEPENDENCIES="python3-mock";

# Exit on error.
set -e;

if test `uname -s` = "Darwin";
then
	git clone https://github.com/log2timeline/l2tdevtools.git;

	mv l2tdevtools ../;
	mkdir dependencies;

	PYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py --download-directory=dependencies ${L2TBINARIES_DEPENDENCIES} ${L2TBINARIES_TEST_DEPENDENCIES};

elif test `uname -s` = "Linux";
then
	sudo add-apt-repository ppa:gift/dev -y;
	sudo apt-get update -q;
	sudo apt-get install -y ${COVERALL_DEPENDENCIES} ${PYTHON2_DEPENDENCIES} ${PYTHON2_TEST_DEPENDENCIES} ${PYTHON3_DEPENDENCIES} ${PYTHON3_TEST_DEPENDENCIES};
fi
