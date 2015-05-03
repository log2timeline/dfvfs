#!/bin/bash
# Script that submits a code for code review.

EXIT_FAILURE=1;
EXIT_MISSING_ARGS=2;
EXIT_SUCCESS=0;

SCRIPTNAME=`basename $0`;

BROWSER_PARAM="";
CACHE_PARAM="";
CL_NUMBER="";
USE_CL_FILE=0;

if ! test -f "utils/common.sh";
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

HAVE_GIT_CL=have_git_cl;

if ! ${HAVE_GIT_CL};
then
  while test $# -gt 0;
  do
    case $1 in
    --nobrowser | --no-browser | --no_browser )
      BROWSER_PARAM="--no_oauth2_webbrowser";
      shift;
      ;;

    *)
      CL_NUMBER=$1;
      shift
      ;;
    esac
  done

  if test -z "${CL_NUMBER}";
  then
    if test -f ._code_review_number;
    then
      CL_NUMBER=`cat ._code_review_number`
      RESULT=`echo ${CL_NUMBER} | sed -e 's/[0-9]//g'`;

      if ! test -z "${RESULT}";
      then
        echo "File ._code_review_number exists but contains an incorrect CL number.";

        exit ${EXIT_FAILURE};
      fi
      USE_CL_FILE=1;
    fi
  fi

  if test -z "${CL_NUMBER}";
  then
    echo "Usage: ./${SCRIPTNAME} [--nobrowser] CL_NUMBER";
    echo "";
    echo "  CL_NUMBER: optional change list (CL) number that is to be submitted.";
    echo "             If no CL number is provided the value is read from:";
    echo "             ._code_review_number";
    echo "";
    echo "  --nobrowser: forces upload.py not to open a separate browser";
    echo "               process to obtain OAuth2 credentials for Rietveld";
    echo "               (https://codereview.appspot.com).";
    echo "";

    exit ${EXIT_MISSING_ARGS};
  fi
fi

if ${HAVE_GIT_CL};
then
  if have_master_branch;
  then
    echo "Submit aborted - current branch is master.";

    exit ${EXIT_FAILURE};
  fi

  if ! local_repo_in_sync_with_origin;
  then
    echo "Local repo out of sync with origin: running 'git pull origin master'.":
    git pull origin master

    if test $? -ne 0;
    then
      echo "Submit aborted - unable to run: 'git pull origin master'.";

      exit ${EXIT_FAILURE};
    fi
  fi
else
  if ! have_master_branch;
  then
    echo "Submit aborted - current branch is not master.";

    exit ${EXIT_FAILURE};
  fi

  if have_double_git_status_codes;
  then
    echo "Submit aborted - detected double git status codes."
    echo "Run: 'git stash && git stash pop'.";

    exit ${EXIT_FAILURE};
  fi

  if ! local_repo_in_sync_with_origin;
  then
    echo "Submit aborted - local repo out of sync with origin."
    echo "Run: 'git stash && git pull && git stash pop'.";

    exit ${EXIT_FAILURE};
  fi
fi

if ! linting_is_correct;
then
  echo "Submit aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

if ! tests_pass;
then
  echo "Submit aborted - fix the issues reported by the failing test.";

  exit ${EXIT_FAILURE};
fi

if test -f "utils/update_version.sh";
then
  . utils/update_version.sh
fi

if ${HAVE_GIT_CL};
then
  if have_uncommitted_changes;
  then
    echo "Warning detected uncommitted changes - press Enter to continue or"
    echo "Ctrl^C to stop.";

    read DUMMY
  fi

  git cl push origin/master;

  BRANCH="";
  get_current_branch "BRANCH";

  git checkout master;
  git pull;
  git branch -D ${BRANCH};

else
  URL_CODEREVIEW="https://codereview.appspot.com";

  # Get the description of the change list.
  RESULT=`which json_xs`;

  # TODO: check if curl exists.
  if ! test -z "${RESULT}";
  then
    DESCRIPTION=`curl -s ${URL_CODEREVIEW}/api/${CL_NUMBER} | json_xs | grep '"subject"' | awk -F '"' '{print $(NF-1)}'`;
  else
    DESCRIPTION=`curl ${URL_CODEREVIEW}/${CL_NUMBER}/ -s | grep "Issue ${CL_NUMBER}" | awk -F ':' '{print $2}' | tail -1`;
  fi

  if test -z "${DESCRIPTION}";
  then
    echo "Submit aborted - unable to find change list with number: ${CL_NUMBER}.";

    exit ${EXIT_FAILURE};
  fi

  COMMIT_DESCRIPTION="Code review: ${CL_NUMBER}: ${DESCRIPTION}";
  echo "Submitting ${COMMIT_DESCRIPTION}";

  # Check if we need to set --cache.
  STATUS_CODES=`git status -s | cut -b1,2 | sed 's/\s//g' | sort | uniq`;

  for STATUS_CODE in ${STATUS_CODES};
  do
    if test "${STATUS_CODE}" = "A";
    then
      CACHE_PARAM="--cache";
    fi
  done

  python utils/upload.py \
      --oauth2 ${BROWSER_PARAM} ${CACHE_PARAM} --send_mail -i ${CL_NUMBER} \
      -y -m "Code Submitted." -t "Submitted.";

  git commit -a -m "${COMMIT_DESCRIPTION}";
  git push

  if test -f "~/codereview_upload_cookies";
  then
    curl -b ~/.codereview_upload_cookies ${URL_CODEREVIEW}/${CL_NUMBER}/close -d  ''
  else
    echo "Could not find an authenticated session to codereview. You need to"
    echo "manually close the ticket on the code review site."
  fi

  if ! test -z "${USE_CL_FILE}" && test -f "._code_review_number";
  then
    rm -f ._code_review_number
  fi
fi

exit ${EXIT_SUCCESS};
