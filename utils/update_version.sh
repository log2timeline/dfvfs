#!/bin/bash
# A small helper script to update the version information.
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DATE_VERSION=`date +"%Y%m%d"`;
DATE_DPKG=`date -R`;
EMAIL_DPKG="Log2Timeline <log2timeline-dev@googlegroups.com>";

sed -i -e "s/^\(__version__ = \)'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'$/\1'${DATE_VERSION}'/" dfvfs/__init__.py
sed -i -e "s/^\(python-dfvfs \)([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1)/\1(${DATE_VERSION}-1)/" config/dpkg/changelog
sed -i -e "s/^\( -- ${EMAIL_DPKG}  \).*$/\1${DATE_DPKG}/" config/dpkg/changelog
