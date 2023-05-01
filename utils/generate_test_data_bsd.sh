#!/usr/bin/env bash
#
# Script to generate dfVFS test files on FreeBSD.

EXIT_SUCCESS=0;
EXIT_FAILURE=1;

# Checks the availability of a binary and exits if not available.
#
# Arguments:
#   a string containing the name of the binary
#
assert_availability_binary()
{
	local BINARY=$1;

	which ${BINARY} > /dev/null 2>&1;
	if test $? -ne ${EXIT_SUCCESS};
	then
		echo "Missing binary: ${BINARY}";
		echo "";

		exit ${EXIT_FAILURE};
	fi
}

# Creates test file entries without a symbolic link.
#
# Arguments:
#   a string containing the mount point
#
create_test_file_entries_without_link()
{
	MOUNT_POINT=$1;

	# Create a directory
	mkdir ${MOUNT_POINT}/a_directory;

	cat >${MOUNT_POINT}/a_directory/a_file <<EOT
This is a text file.

We should be able to parse it.
EOT

	cat >${MOUNT_POINT}/passwords.txt <<EOT
place,user,password
bank,joesmith,superrich
alarm system,-,1234
treasure chest,-,1111
uber secret laire,admin,admin
EOT

	cat >${MOUNT_POINT}/a_directory/another_file <<EOT
This is another file.
EOT
}

# Creates test file entries.
#
# Arguments:
#   a string containing the mount point
#
create_test_file_entries()
{
	MOUNT_POINT=$1;

	create_test_file_entries_without_link ${MOUNT_POINT}

	(cd ${MOUNT_POINT} && ln -s a_directory/another_file a_link);
}

assert_availability_binary bsdlabel;
assert_availability_binary dd;
assert_availability_binary mdconfig;
assert_availability_binary newfs;

set -e;

mkdir -p test_data;

MOUNT_POINT="/mnt/dfvfs";

IMAGE_SIZE=$(( 4 * 1024 * 1024 ));
SECTOR_SIZE=512;

mkdir -p ${MOUNT_POINT};

# Create test image with an UFS1 file system
IMAGE_FILE="test_data/ufs1.raw";

dd if=/dev/zero of=${IMAGE_FILE} bs=${SECTOR_SIZE} count=$(( ${IMAGE_SIZE} / ${SECTOR_SIZE} )) 2> /dev/null;

mdconfig -a -t vnode -f ${IMAGE_FILE} -u 9;

bsdlabel -w -B md9 auto;

newfs -L "ufs1_test" -O 1 md9a;

mount /dev/md9a ${MOUNT_POINT};

create_test_file_entries ${MOUNT_POINT};

umount ${MOUNT_POINT};

mdconfig -d -u 9;

# Create test image with an UFS2 file system
IMAGE_FILE="test_data/ufs2.raw";

dd if=/dev/zero of=${IMAGE_FILE} bs=${SECTOR_SIZE} count=$(( ${IMAGE_SIZE} / ${SECTOR_SIZE} )) 2> /dev/null;

mdconfig -a -t vnode -f ${IMAGE_FILE} -u 9;

bsdlabel -w -B md9 auto;

newfs -L "ufs2_test" -O 2 md9a;

mount /dev/md9a ${MOUNT_POINT};

create_test_file_entries ${MOUNT_POINT};

umount ${MOUNT_POINT};

mdconfig -d -u 9;

