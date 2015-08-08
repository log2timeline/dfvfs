#!/bin/bash
# Script that submits a code for code review.

EXIT_SUCCESS=0;
EXIT_MISSING_ARGS=2;
EXIT_SUCCESS=0;

SCRIPTNAME=`basename $0`;
NETRC="${HOME}/.netrc";

BROWSER_PARAM="";
USE_CL_FILE=1;
CL_FILENAME="";
BRANCH="";

if test -e ".review" && ! test -d ".review";
then
  echo "Unable to find common scripts (utils/common.sh).";
  echo "This script can only be run from the root of the source directory.";

  exit ${EXIT_FAILURE};
fi

if ! test -f "utils/common.sh";
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

if ! have_curl;
then
  echo "You'll need to install curl for this script to continue.";

  exit ${EXIT_FAILURE};
fi

if ! test -f "${NETRC}";
then
  echo "No such file: ${NETRC}";

  exit ${EXIT_FAILURE};
fi

ACCESS_TOKEN=`grep 'github.com' ${NETRC} | awk '{ print $6 }'`;

if test -z "${ACCESS_TOKEN}";
then
  echo "Unable to determine github.com access token from: ${NETRC}";

  exit ${EXIT_FAILURE};
fi

# TODO: add diffbase support?

# Determine if we have the master repo as origin.
HAVE_REMOTE_ORIGIN=have_remote_origin;

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
    REVIEWERS=$1;
    shift
    ;;
  esac
done

if test -z "${REVIEWERS}";
then
  echo "Usage: ./${SCRIPTNAME} [--nobrowser] [--noclfile] REVIEWERS";
  echo "";
  echo "  REVIEWERS: the email address of the reviewers that are registered"
  echo "             with: Rietveld (https://codereview.appspot.com)";
  echo "";
  echo "  --nobrowser: forces upload.py not to open a separate browser";
  echo "               process to obtain OAuth2 credentials for Rietveld";
  echo "               (https://codereview.appspot.com).";
  echo "";
  echo "  --noclfile: do not store the resulting CL number in a CL file"
  echo "              stored in .review/";
  echo "";

  exit ${EXIT_MISSING_ARGS};
fi

if ! ${HAVE_REMOTE_ORIGIN};
then
  if ! have_remote_upstream;
  then
    echo "Review aborted - missing upstream.";
    echo "Run: 'git remote add upstream https://github.com/log2timeline/dfvfs.git'";

    exit ${EXIT_FAILURE};
  fi
  git fetch upstream;

  if have_master_branch;
  then
    echo "Review aborted - current branch is master.";

    exit ${EXIT_FAILURE};
  fi

  if have_uncommitted_changes;
  then
    echo "Review aborted - detected uncommitted changes.";

    exit ${EXIT_FAILURE};
  fi

  if ! local_repo_in_sync_with_upstream;
  then
    echo "Local repo out of sync with upstream: running 'git pull --rebase upstream master'.":
    git pull --rebase upstream master

    if test $? -ne 0;
    then
      echo "Review aborted - unable to run: 'git pull --rebase upstream master'.";

      exit ${EXIT_FAILURE};
    fi
  fi

  if ! linter_pass;
  then
    echo "Review aborted - fix the issues reported by the linter.";

    exit ${EXIT_FAILURE};
  fi

else
  if have_double_git_status_codes;
  then
    echo "Review aborted - detected double git status codes."
    echo "Run: 'git stash && git stash pop'.";

    exit ${EXIT_FAILURE};
  fi

  if ! linting_is_correct;
  then
    echo "Review aborted - fix the issues reported by the linter.";

    exit ${EXIT_FAILURE};
  fi
fi

if ! tests_pass;
then
  echo "Review aborted - fix the issues reported by the failing test.";

  exit ${EXIT_FAILURE};
fi

if test ${USE_CL_FILE} -ne 0;
then
  get_current_branch "BRANCH";

  CL_FILENAME=".review/${BRANCH}";

  if test -f ${CL_FILENAME};
  then
    echo "Review aborted - CL file already exitst: ${CL_FILENAME}";
    echo "Do you already have a code review pending for the current branch?";

    exit ${EXIT_FAILURE};
  fi
fi

if ! ${HAVE_REMOTE_ORIGIN};
then
  get_current_branch "BRANCH";

  git push --set-upstream origin ${BRANCH};

  if test $? -ne 0;
  then
    echo "Unable to push to origin";
    echo "";

    exit ${EXIT_FAILURE};
  fi

  DESCRIPTION="";
  get_last_change_description "DESCRIPTION";

  if ! test -z "${BROWSER_PARAM}";
  then
    echo "You need to visit: https://codereview.appspot.com/get-access-token";
    echo "and copy+paste the access token to the window (no prompt)";
  fi

  TEMP_FILE=`mktemp .tmp_dfvfs_code_review.XXXXXX`;

  python utils/upload.py \
      --oauth2 ${BROWSER_PARAM} \
      --send_mail -r ${REVIEWERS} --cc log2timeline-dev@googlegroups.com \
      -t "${DESCRIPTION}" -y -- upstream/master | tee ${TEMP_FILE};

  CL=`cat ${TEMP_FILE} | grep codereview.appspot.com | awk -F '/' '/created/ {print $NF}'`;
  cat ${TEMP_FILE};
  rm -f ${TEMP_FILE};

  if test -z ${CL};
  then
    echo "Unable to upload code change for review.";

    exit ${EXIT_FAILURE};
  fi

  if test -z "${BRANCH}";
  then
    get_current_branch "BRANCH";
  fi

  ORGANIZATION=`git remote -v | grep 'origin' | sed 's?^.*https://github.com/\([^/]*\)/.*$?\1?' | sort | uniq`;

  POST_DATA="{
  \"title\": \"${DESCRIPTION}\",
  \"body\": \"[Code review: ${CL}: ${DESCRIPTION}](https://codereview.appspot.com/${CL}/)\",
  \"head\": \"${ORGANIZATION}:${BRANCH}\",
  \"base\": \"master\"
}";

  echo "Creating pull request.";
  curl -s --data "${POST_DATA}" https://api.github.com/repos/log2timeline/dfvfs/pulls?access_token=${ACCESS_TOKEN} >/dev/null;

  if test $? -ne 0;
  then
    echo "Unable to create pull request.";
    echo "";

    exit ${EXIT_FAILURE};
  fi

else
  echo -n "Short description of code review request: ";
  read DESCRIPTION

  # Check if we need to set --cache.
  STATUS_CODES=`git status -s | cut -b1,2 | sed 's/\s//g' | sort | uniq`;

  CACHE_PARAM="";
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

  TEMP_FILE=`mktemp .tmp_dfvfs_code_review.XXXXXX`;

  python utils/upload.py \
      --oauth2 ${BROWSER_PARAM} ${CACHE_PARAM} \
      --send_mail -r ${REVIEWERS} --cc log2timeline-dev@googlegroups.com \
      -m "${DESCRIPTION}" -t "${DESCRIPTION}" -y | tee ${TEMP_FILE};

  CL=`cat ${TEMP_FILE} | grep codereview.appspot.com | awk -F '/' '/created/ {print $NF}'`;
  cat ${TEMP_FILE};
  rm -f ${TEMP_FILE};

  if test -z ${CL};
  then
    echo "Unable to upload code change for review.";

    exit ${EXIT_FAILURE};
  fi
fi

if test ${USE_CL_FILE} -ne 0;
then
  if ! test -e ".review";
  then
    mkdir .review;
  fi

  echo ${CL} > ${CL_FILENAME};

  echo "";
  echo "Saved code review number for future updates.";
fi

exit ${EXIT_SUCCESS};
