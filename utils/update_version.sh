#!/bin/bash
# Script to update the version information.

DATE_VERSION=`date +"%Y%m%d"`;
DATE_DPKG=`date -R`;
EMAIL_DPKG="Log2Timeline <log2timeline-dev@googlegroups.com>";

sed -i -e "s/^\(__version__ = \)'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'$/\1'${DATE_VERSION}'/" dfvfs/__init__.py
sed -i -e "s/^\(python-dfvfs \)([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1)/\1(${DATE_VERSION}-1)/" config/dpkg/changelog
sed -i -e "s/^\( -- ${EMAIL_DPKG}  \).*$/\1${DATE_DPKG}/" config/dpkg/changelog
