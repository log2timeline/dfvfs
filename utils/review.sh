#!/bin/bash
# A small script that submits a code for code review.
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

EXIT_SUCCESS=0;
EXIT_MISSING_ARGS=2;
EXIT_SUCCESS=0;

SCRIPTNAME=`basename $0`;

BROWSER_PARAM="";
CACHE_PARAM="";
USE_CL_FILE=1;

if ! test -f "utils/common.sh";
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

HAVE_GIT_CL=have_git_cl;

if ${HAVE_GIT_CL};
then
  while test $# -gt 0;
  do
    case $1 in
    *)
      REVIEWER=$1;
      shift
      ;;
    esac
  done

  if test -z "${REVIEWER}";
  then
    echo "Usage: ./${SCRIPTNAME} REVIEWER";
    echo "";
    echo "  REVIEWER: the email address of the reviewer that is registered with:"
    echo "            Rietveld (https://codereview.appspot.com)";
    echo "";

    exit ${EXIT_MISSING_ARGS};
  fi
else
  while test $# -gt 0;
  do
    case $1 in
    --nobrowser | --no-browser | --no_browser )
      BROWSER_PARAM="--no_oauth2_webbrowser";
      shift;
      ;;

    --noclfile | --no-clfile | --no_clfile )
      USE_CL_FILE=0;
      shift;
      ;;

    *)
      REVIEWER=$1;
      shift
      ;;
    esac
  done

  if test -z "${REVIEWER}";
  then
    echo "Usage: ./${SCRIPTNAME} [--nobrowser] [--noclfile] REVIEWER";
    echo "";
    echo "  REVIEWER: the email address of the reviewer that is registered with:"
    echo "            https://codereview.appspot.com";
    echo "";
    echo "  --nobrowser: forces upload.py not to open a separate browser";
    echo "               process to obtain OAuth2 credentials for Rietveld";
    echo "               (https://codereview.appspot.com)).";
    echo "";
    echo "  --noclfile: do not store the resulting CL number in a file named:"
    echo "              ._code_review_number";
    echo "";

    exit ${EXIT_MISSING_ARGS};
  fi
fi

if ${HAVE_GIT_CL};
then
  if have_master_branch;
  then
    echo "Review upload aborted - current branch is master.";

    exit ${EXIT_FAILURE};
  fi

  if ! local_repo_in_sync_with_origin;
  then
    echo "Local repo out of sync with origin: running 'git pull origin master'.":
    git pull origin master

    if test $? -ne 0;
    then
      echo "Review upload aborted - unable to run: 'git pull origin master'.";

      exit ${EXIT_FAILURE};
    fi
  fi
else
  if have_double_git_status_codes:
  then
    echo "Review upload aborted - detected double git status codes."
    echo "Run: 'git stash && git stash pop'.";

    exit ${EXIT_FAILURE};
  fi
fi

if ! linting_is_correct;
then
  echo "Review upload aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

if ! tests_pass;
then
  echo "Review upload aborted - fix the issues reported by the failing test.";

  exit ${EXIT_FAILURE};
fi

if ${HAVE_GIT_CL};
then
  if have_uncommitted_changes;
  then
    echo "Warning detected uncommitted changes - press Enter to continue or"
    echo "Ctrl^C to stop.";

    read DUMMY
  fi
  DESCRIPTION="";
  get_last_change_description "DESCRIPTION";

  git cl upload --send-mail \
      -r ${REVIEWER} --cc=log2timeline-dev@googlegroups.com \
      -f -m "Code updated for review." -t "${DESCRIPTION}" origin/master;

else
  MISSING_TESTS="";
  FILES=`git status -s | grep -v "^?" | awk '{if ($1 != 'D') { print $2;}}' | grep "\.py$" | grep -v "_test.py$"`
  for CHANGED_FILE in ${FILES};
  do
    TEST_FILE=`echo ${CHANGED_FILE} | sed -e 's/\.py//g'`
    if ! test -f "${TEST_FILE}_test.py";
    then
      MISSING_TESTS="${MISSING_TESTS} + ${CHANGED_FILE}"
    fi
  done

  if test -z "${MISSING_TESTS}";
  then
    MISSING_TEST_FILES=".";
  else
    MISSING_TEST_FILES="These files are missing unit tests:
  ${MISSING_TESTS}
    ";
  fi

  echo -n "Short description of code review request: ";
  read DESCRIPTION
  TEMP_FILE=`mktemp .tmp_dfvfs_code_review.XXXXXX`;

  # Check if we need to set --cache.
  STATUS_CODES=`git status -s | cut -b1,2 | sed 's/\s//g' | sort | uniq`;

  for STATUS_CODE in ${STATUS_CODES};
  do
    if test "${STATUS_CODE}" = "A";
    then
      CACHE_PARAM="--cache";
    fi
  done

  if ! test -z "${BROWSER_PARAM}";
  then
    echo "You need to visit: https://codereview.appspot.com/get-access-token";
    echo "and copy+paste the access token to the window (no prompt)";
  fi

  python utils/upload.py \
      --oauth2 ${BROWSER_PARAM} ${CACHE_PARAM} --send_mail \
      -r ${REVIEWER} --cc log2timeline-dev@googlegroups.com \
      -y -m "${MISSING_TEST_FILES}" -t "${DESCRIPTION}" | tee ${TEMP_FILE};

  CL=`cat ${TEMP_FILE} | grep codereview.appspot.com | awk -F '/' '/created/ {print $NF}'`;
  cat ${TEMP_FILE};
  rm -f ${TEMP_FILE};

  echo "";

  if test -z ${CL};
  then
    echo "Unable to upload code change for review.";
    exit ${EXIT_FAILURE};

  elif test ${USE_CL_FILE} -ne 0;
  then
    echo ${CL} > ._code_review_number;
    echo "Code review number: ${CL} is saved, so no need to include that in future updates/submits.";
  fi
fi

exit ${EXIT_SUCCESS};
