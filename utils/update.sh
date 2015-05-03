#!/bin/bash
# Script that updates a change list for code review.

EXIT_FAILURE=1;
EXIT_MISSING_ARGS=2;
EXIT_SUCCESS=0;

SCRIPTNAME=`basename $0`;

BROWSER_PARAM="";
CACHE_PARAM="";
CL_NUMBER="";

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
    fi
  fi

  if test -z "${CL_NUMBER}";
  then
    echo "Usage: ./${SCRIPTNAME} [--nobrowser] [CL_NUMBER]";
    echo "";
    echo "  CL_NUMBER: optional change list (CL) number that is to be updated.";
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
    echo "Update upload aborted - current branch is master.";

    exit ${EXIT_FAILURE};
  fi

  if ! local_repo_in_sync_with_origin;
  then
    echo "Local repo out of sync with origin: running 'git pull origin master'.":
    git pull origin master

    if test $? -ne 0;
    then
      echo "Update upload aborted - unable to run: 'git pull origin master'.";

      exit ${EXIT_FAILURE};
    fi
  fi
else
  if have_double_git_status_codes;
  then
    echo "Update upload aborted - detected double git status codes."
    echo "Run: 'git stash && git stash pop'.";

    exit ${EXIT_FAILURE};
  fi
fi

if ! linting_is_correct;
then
  echo "Update upload aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

if ! tests_pass;
then
  echo "Update upload aborted - fix the issues reported by the failing test.";

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

  git cl upload -f -m "Code updated." -t "${DESCRIPTION}" origin/master;

else
  if have_uncommitted_changes_with_append_status;
  then
    CACHE_PARAM="--cache";
  fi
  echo -n "Short description of the update: ";
  read DESCRIPTION

  python utils/upload.py \
      --oauth2 ${BROWSER_PARAM} ${CACHE_PARAM} -i ${CL_NUMBER} \
      -y -m "Code updated." -t "${DESCRIPTION}";
fi

exit ${EXIT_SUCCESS};
