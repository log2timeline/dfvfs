#!/bin/bash
# Script that runs the linter on all files.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

if [ ! -f "utils/common.sh" ];
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

if ! linting_is_correct;
then
  echo "Aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

# Determine if we have the master repo as origin.
HAVE_REMOTE_ORIGIN=have_remote_origin;

if ! ${HAVE_REMOTE_ORIGIN};
then
  if ! have_remote_upstream;
  then
    echo "Review upload aborted - missing upstream.";
    echo "Run: 'git remote add upstream https://github.com/log2timeline/dfvfs.git'";

    exit ${EXIT_FAILURE};
  fi

  if ! linter_pass;
  then
    echo "Aborted - fix the issues reported by the linter.";

    exit ${EXIT_FAILURE};
  fi
fi

exit ${EXIT_SUCCESS};

