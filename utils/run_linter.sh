#!/bin/bash
# Script that runs the linter on all files.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

if ! test -f "utils/common.sh";
then
  echo "Unable to find common scripts (utils/common.sh).";
  echo "This script can only be run from the root of the source directory.";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

if ! linting_is_correct;
then
  echo "Linting aborted - fix the reported issues.";

  exit ${EXIT_FAILURE};
fi

# Determine if we have the master repo as origin.
HAVE_REMOTE_ORIGIN=have_remote_origin;

if ! ${HAVE_REMOTE_ORIGIN};
then
  if ! have_remote_upstream;
  then
    echo "Linting aborted - missing upstream.";
    echo "Run: 'git remote add upstream https://github.com/log2timeline/dfvfs.git'";

    exit ${EXIT_FAILURE};
  fi
  git fetch upstream;

  if ! linter_pass;
  then
    echo "Linting aborted - fix the reported issues.";

    exit ${EXIT_FAILURE};
  fi
fi

exit ${EXIT_SUCCESS};

