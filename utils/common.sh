#!/bin/bash
# A small script that contains common functions for code review checks.
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

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

FALSE=1;
TRUE=0;

# Function to check for double status codes rietveld does not seem to handle
# these correctly.
have_double_git_status_codes()
{
  STATUS_CODES=`git status -s | cut -b1,2 | grep '\S\S' | grep -v '??' | sort | uniq`;

  if ! test -z "${STATUS_CODES}";
  then
    return ${TRUE};
  fi
  return ${FALSE};
}

# Function to check if we have "git cl" or that we should use upload.py instead.
have_git_cl()
{
  DUMMY=`git cl 2> /dev/null`;

  if test $? -eq 0;
  then
    return ${TRUE};
  fi
  return ${FALSE};
}

# Function to check if we are on the master branch.
have_master_branch()
{
  BRANCH="";
  get_current_branch "BRANCH";

  if test "${BRANCH}" = "master";
  then
    return ${TRUE};
  fi
  return ${FALSE};
}

# Function to check if we have uncommitted changes.
have_uncommitted_changes()
{
  # Ignore the '??' status code.
  GIT_STATUS=`git status -s | grep -v -e '^?? '`;

  if test -z "${GIT_STATUS}";
  then
    return ${FALSE};
  fi
  return ${TRUE};
}

# Function to check if we have uncommitted changes with new files.
have_uncommitted_changes_with_append_status()
{
  RESULT=${FALSE};
  STATUS_CODES=`git status -s | cut -b1,2 | sed 's/\s//g' | sort | uniq`;

  for STATUS_CODE in ${STATUS_CODES};
  do
    if test "${STATUS_CODE}" = "A";
    then
      RESULT=${TRUE};
    fi
  done
  return ${RESULT};
}

# Function to retrieve the name of the current branch.
get_current_branch()
{
  RESULT=`git branch | grep -e "^[*]" | sed "s/^[*] //"`;
  eval "$1='${RESULT}'";
}

# Function to retrieve the desciption of the last committed change.
get_last_change_description()
{
  RESULT=`git log | head -n5 | tail -n1 | sed 's/^[ ]*//'`;
  eval "$1='${RESULT}'";
}

# Function to check if the linting of the changes is correct.
linting_is_correct()
{
  # Examples of the output of "git status -s"
  # If a file is added:
  # A utils/common.sh
  # If a file is modified:
  # M utils/common.sh
  # If a file is renamed:
  # R utils/common.sh -> utils/uncommon.sh
  # If a file is modified and renamed:
  # RM utils/common.sh -> utils/uncommon.sh
  AWK_SCRIPT="if (\$1 == \"A\" || \$1 == \"AM\" || \$1 == \"M\") { print \$2; } else if (\$1 == \"R\" || \$1 == \"RM\") { print \$4; }";

  # First find all files that need linter
  FILES=`git status -s | grep -v "^?" | awk "{ ${AWK_SCRIPT} }" | grep "\.py$"`;

  LINTER="pylint --rcfile=utils/pylintrc"

  echo "Running changes by pylint.";

  for FILE in ${FILES};
  do
    if test "${FILE}" = "setup.py" || test "${FILE}" = "utils/upload.py";
    then
      echo "  -- Skipping: ${FILE} --"
      continue
    fi

    if test `echo ${FILE} | tail -c8` == "_pb2.py";
    then
      echo "Skipping compiled protobufs: ${FILE}"
      continue
    fi

    echo "  -- Checking: ${FILE} --"
    ${LINTER} "${FILE}"

    if test $? -ne 0;
    then
      echo "Fix linter errors before proceeding."
      return ${FALSE};
    fi
  done

  if test $? -ne 0;
  then
    return ${FALSE};
  fi

  echo "Linter clear.";

  return ${TRUE};
}

# Function to check if the local repo is in sync with the origin.
local_repo_in_sync_with_origin()
{
  git fetch

  if test $? -ne 0;
  then
    echo "Unable to fetch updates from origin.";

    exit ${EXIT_FAILURE};
  fi
  NUMBER_OF_CHANGES=`git log HEAD..origin/master --oneline | wc -l`;

  if test $? -ne 0;
  then
    echo "Unable to determine if local repo is in sync with origin.";

    exit ${EXIT_FAILURE};
  fi

  if test ${NUMBER_OF_CHANGES} -eq 0;
  then
    return ${TRUE};
  fi
  return ${FALSE};
}

# Function to check if the tests pass.
# Note that the function will also return true (0) if the run_tests.py script
# cannot be found.
tests_pass()
{
  if ! test -e run_tests.py;
  then
    return ${TRUE};
  fi

  echo "Running tests.";
  python run_tests.py

  if test $? -eq 0;
  then
    return ${TRUE};
  fi
  return ${FALSE};
}
